"""
Routes API Click & Collect.
"""
from flask import request

from services import (
    create_session,
    get_session,
    update_session,
    delete_session,
    save_click_order_history_snapshot,
    update_click_order_history_status,
)
from utils.responses import (
    success_response,
    error_response,
    ErrorCode,
    handle_api_errors,
)


def _require_session(panier_id: str):
    """Retourne la session ou (None, error_response)."""
    session = get_session(panier_id)
    if session is None:
        return None, error_response(
            ErrorCode.SESSION_NOT_FOUND,
            http_status=404,
        )
    return session, None


def register_routes(app):
    """Enregistre les routes sur l'app Flask."""

    @app.route("/stores", methods=["GET"])
    @handle_api_errors
    def get_stores():
        """
        GET /stores?city=Paris - Liste les KFC par ville.
        Retourne [{id, name, city}, ...]. Pas de session requise.
        """
        city = request.args.get("city")
        if not city:
            return error_response(
                ErrorCode.VALIDATION_ERROR,
                message="Le paramètre 'city' est requis",
                http_status=400,
            )

        try:
            from ressource.kfc_api import stores
            from ressource import cities
        except ImportError:
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Module KFC indisponible",
                http_status=502,
            )

        all_stores = stores.GetAllStores()
        if all_stores is None:
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Impossible de récupérer la liste des restaurants",
                http_status=502,
            )

        matched = cities.GetMatchingPlace2(all_stores, city)
        if matched is None:
            return success_response([])

        stores_list = [
            {"id": s[2], "name": s[0], "city": s[1]}
            for s in matched
        ]
        return success_response(stores_list)

    @app.route("/accounts/balance", methods=["GET"])
    @handle_api_errors
    def get_account_balance():
        """
        GET /accounts/balance?account_id=...&account_token=...
        Récupère le solde de points fidélité du compte KFC.
        Retourne { "balance": int }.
        """
        account_id = request.args.get("account_id")
        account_token = request.args.get("account_token")
        if not account_id or not account_token:
            return error_response(
                ErrorCode.VALIDATION_ERROR,
                message="Les paramètres account_id et account_token sont requis",
                http_status=400,
            )
        try:
            from ressource.account import GetAccountLoyaltyInfo
        except ImportError:
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Module KFC indisponible",
                http_status=502,
            )
        loyalty_info = GetAccountLoyaltyInfo(account_id, account_token)
        if loyalty_info is None:
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Impossible de récupérer les infos fidélité du compte",
                http_status=502,
            )
        balance = loyalty_info.get("loyaltyPoints") or loyalty_info.get("loyalty_points") or loyalty_info.get("points")
        if balance is None:
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Solde de points introuvable dans la réponse KFC",
                http_status=502,
            )
        try:
            balance = int(balance)
        except (TypeError, ValueError):
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Format de solde invalide",
                http_status=502,
            )
        return success_response({"balance": balance})

    @app.route("/stores/<store_id>/preview-menu", methods=["GET"])
    @handle_api_errors
    def get_stores_preview_menu(store_id):
        """
        GET /stores/<store_id>/preview-menu?account_id=...&account_token=...
        Menu fidélité du restaurant (sans session).
        Le bot fournit account_id et account_token dans la requête.
        Retourne { categories: { "Mega Deals": [...], ... } }.
        """
        account_id = request.args.get("account_id")
        account_token = request.args.get("account_token")
        if not account_id or not account_token:
            return error_response(
                ErrorCode.VALIDATION_ERROR,
                message="Les paramètres account_id et account_token sont requis",
                http_status=400,
            )
        try:
            from ressource import loyalty
        except ImportError:
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Module KFC indisponible",
                http_status=502,
            )
        from ressource.account import GetAccountLoyaltyInfo
        loyalty_info = GetAccountLoyaltyInfo(account_id, account_token)
        if loyalty_info is None:
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Impossible de récupérer les infos fidélité du compte",
                http_status=502,
            )
        store_loyalty = loyalty.GetLoyaltyFromStore(store_id)
        if store_loyalty is None:
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Impossible de récupérer le menu du restaurant",
                http_status=502,
            )
        loyalty_info_rewards = loyalty_info.get("rewards")
        if not loyalty_info_rewards:
            return success_response({"categories": {}})
        menu, matched_count = loyalty.LoyaltyMatch(loyalty_info_rewards, store_loyalty)
        # Ancienne logique : strictement == LOYALTY_MATCH_COUNT_SUPPORTED (35).
        # Nouvelle logique : on considère le KFC comme éligible si matched_count > 30,
        # pour être plus tolérant aux variations de menu côté KFC.
        if matched_count is None or matched_count <= 30:
            return error_response(
                ErrorCode.STORE_NOT_SUPPORTED,
                message=(
                    "Le Click & Collect de ce KFC contient des bugs côté KFC, "
                    "il vaut mieux en choisir un autre."
                ),
                details={"matched_items": matched_count, "required": loyalty.LOYALTY_MATCH_COUNT_SUPPORTED},
                http_status=400,
            )
        return success_response({"categories": menu})

    @app.route("/modgrps/build-from-tree", methods=["POST"])
    @handle_api_errors
    def post_modgrps_build_from_tree():
        """
        POST /modgrps/build-from-tree - Construit la liste modgrps pour KFC depuis l'arbre rempli (qty déjà set).
        Body: { "tree": [ ... ] } (arbre modgrps muté en place par le bot).
        """
        data = request.get_json() or {}
        tree = data.get("tree", [])

        try:
            app.logger.info(
                "/modgrps/build-from-tree request tree_groups=%s first_group_ids=%s",
                len(tree or []),
                [g.get("id") for g in (tree or [])[:5]],
            )
        except Exception:
            pass

        if not tree:
            return success_response({"modgrps": []})

        try:
            from ressource import modgrps as modgrps_module
            result = modgrps_module.build_modgrps_from_tree(tree)
            try:
                app.logger.info(
                    "/modgrps/build-from-tree OK built_groups=%s example=%s",
                    len(result or []),
                    (result or [])[:1],
                )
            except Exception:
                pass
            return success_response({"modgrps": result})
        except Exception as e:
            app.logger.exception("Erreur lors de la construction des modgrps")
            return error_response(
                ErrorCode.VALIDATION_ERROR,
                message="Erreur lors de la construction des modgrps",
                details={"detail": str(e)},
                http_status=400,
            )

    @app.route("/sessions", methods=["POST"])
    @handle_api_errors
    def post_sessions():
        """POST /sessions - Créer une session."""
        data = request.get_json() or {}
        panier_id = data.get("panier_id")
        account_id = data.get("account_id")
        account_token = data.get("account_token")
        store_id = data.get("store_id")
        balance_user = data.get("balance_user")
        store_name = data.get("store_name")
        store_city = data.get("store_city")
        telegram_id = data.get("telegram_id")
        create_basket = data.get("create_basket", True)

        if not panier_id or not account_id or not account_token or not store_id:
            return error_response(
                ErrorCode.VALIDATION_ERROR,
                message="panier_id, account_id, account_token et store_id sont requis",
                http_status=400,
            )

        if balance_user is None:
            # Récupérer le solde depuis l'API KFC
            try:
                from ressource.account import GetAccountLoyaltyInfo
                loyalty_info = GetAccountLoyaltyInfo(account_id, account_token)
                if loyalty_info is None:
                    return error_response(
                        ErrorCode.KFC_API_ERROR,
                        message="Impossible de récupérer le solde du compte KFC",
                        http_status=502,
                    )
                balance_user = loyalty_info.get("loyaltyPoints") or loyalty_info.get("loyalty_points") or loyalty_info.get("points")
                if balance_user is None:
                    return error_response(
                        ErrorCode.KFC_API_ERROR,
                        message="Solde de points introuvable dans la réponse KFC",
                        http_status=502,
                    )
                balance_user = int(balance_user)
            except (TypeError, ValueError):
                return error_response(
                    ErrorCode.KFC_API_ERROR,
                    message="Format de solde invalide",
                    http_status=502,
                )
            except ImportError:
                return error_response(
                    ErrorCode.VALIDATION_ERROR,
                    message="balance_user est requis (int) ou fournissez account_id/account_token valides",
                    http_status=400,
                )
        else:
            try:
                balance_user = int(balance_user)
            except (TypeError, ValueError):
                return error_response(
                    ErrorCode.VALIDATION_ERROR,
                    message="balance_user doit être un entier",
                    http_status=400,
                )
        if balance_user < 0:
            return error_response(
                ErrorCode.VALIDATION_ERROR,
                message="balance_user doit être >= 0",
                http_status=400,
            )

        # Vérification : le restaurant est-il supporté pour le Click & Collect ? (avant création)
        if create_basket:
            try:
                from ressource import loyalty
                match_count = loyalty.GetStoreLoyaltyMatchCount(
                    account_id, store_id, account_token
                )
                # Nouvelle logique : on considère le KFC comme éligible si match_count > 30
                if match_count is not None and match_count <= 30:
                    return error_response(
                        ErrorCode.STORE_NOT_SUPPORTED,
                        message="Ce restaurant n'est pas supporté pour le Click & Collect",
                        details={
                            "matched_items": match_count,
                            "required_min": 31,
                            "required": loyalty.LOYALTY_MATCH_COUNT_SUPPORTED,
                        },
                        http_status=400,
                    )
            except ImportError:
                pass  # Si module indisponible, on ne bloque pas

        session, err_code = create_session(
            panier_id=panier_id,
            account_id=account_id,
            account_token=account_token,
            store_id=store_id,
            balance_user=balance_user,
            store_name=store_name,
            store_city=store_city,
            telegram_id=telegram_id,
            create_basket=create_basket,
        )

        if err_code == "SESSION_ALREADY_EXISTS":
            return error_response(
                ErrorCode.SESSION_ALREADY_EXISTS,
                http_status=409,
            )
        if err_code == "KFC_API_ERROR":
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Impossible de créer le panier KFC",
                http_status=502,
            )

        return success_response(session.to_dict(), http_status=201)

    @app.route("/sessions/<panier_id>", methods=["GET"])
    @handle_api_errors
    def get_sessions(panier_id):
        """GET /sessions/<panier_id> - Récupérer une session."""
        session, err = _require_session(panier_id)
        if err:
            return err
        return success_response(session.to_dict())

    @app.route("/sessions/<panier_id>/store", methods=["GET"])
    @handle_api_errors
    def get_session_store(panier_id):
        """GET /sessions/<panier_id>/store - Infos du KFC de la session."""
        session, err = _require_session(panier_id)
        if err:
            return err
        return success_response({
            "store_id": session.store_id,
            "store_name": session.store_name,
            "store_city": session.store_city,
        })

    @app.route("/sessions/<panier_id>/stores", methods=["GET"])
    @handle_api_errors
    def get_session_stores(panier_id):
        """GET /sessions/<panier_id>/stores - Liste des KFC (?city= pour filtrer)."""
        city = request.args.get("city")
        try:
            from ressource.kfc_api import stores
            from ressource import cities
        except ImportError:
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Module KFC indisponible",
                http_status=502,
            )

        all_stores = stores.GetAllStores()
        if all_stores is None:
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Impossible de récupérer la liste des restaurants",
                http_status=502,
            )

        if city:
            matched = cities.GetMatchingPlace2(all_stores, city)
            if matched is None:
                return success_response([])
            stores_list = [
                {"id": s[2], "name": s[0], "city": s[1]}
                for s in matched
            ]
        else:
            stores_list = [
                {"id": s["id"], "name": s.get("name", ""), "city": s.get("city", "")}
                for s in all_stores
            ]

        return success_response(stores_list)

    @app.route("/sessions/<panier_id>/loyalty-menu", methods=["GET"])
    @handle_api_errors
    def get_session_loyalty_menu(panier_id):
        """GET /sessions/<panier_id>/loyalty-menu - Menu fidélité du restaurant."""
        session, err = _require_session(panier_id)
        if err:
            return err

        try:
            from ressource import loyalty
        except ImportError:
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Module KFC indisponible",
                http_status=502,
            )

        menu = loyalty.GetLoyaltyMenu(
            session.account_id,
            session.store_id,
            session.account_token,
        )
        if menu is None:
            return error_response(
                ErrorCode.LOYALTY_MENU_UNAVAILABLE,
                http_status=502,
            )

        return success_response(menu)

    @app.route("/sessions/<panier_id>/basket", methods=["GET"])
    @handle_api_errors
    def get_session_basket(panier_id):
        """GET /sessions/<panier_id>/basket - Contenu du panier."""
        session, err = _require_session(panier_id)
        if err:
            return err

        if not session.basket_id:
            return success_response({"items": [], "total": 0})

        try:
            from ressource import basket
        except ImportError:
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Module KFC indisponible",
                http_status=502,
            )

        basket_data = basket.GetBasketById(session.basket_id)
        if basket_data is None:
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Impossible de récupérer le panier",
                http_status=502,
            )

        return success_response(basket_data)

    @app.route("/sessions/<panier_id>/basket/items", methods=["POST"])
    @handle_api_errors
    def post_basket_items(panier_id):
        """POST /sessions/<panier_id>/basket/items - Ajouter un article fidélité."""
        session, err = _require_session(panier_id)
        if err:
            return err

        if session.status != "DRAFT":
            return error_response(
                ErrorCode.INVALID_STATE,
                message="Seules les sessions DRAFT permettent d'ajouter des articles",
                details={"current_status": session.status},
                http_status=400,
            )

        if not session.basket_id:
            return error_response(
                ErrorCode.INVALID_STATE,
                message="Aucun panier associé à cette session",
                http_status=400,
            )

        data = request.get_json() or {}
        loyalty_id = data.get("loyalty_id")
        cost = data.get("cost", 0)
        quantity = data.get("quantity", 1)
        modgrps = data.get("modgrps")
        if modgrps is None:
            modgrps = []

        name = data.get("name")

        try:
            import json as _json
            app.logger.info(
                "/sessions/%s/basket/items request loyalty_id=%s name=%s cost=%s quantity=%s modgrps_groups=%s modgrps_raw=%s",
                panier_id,
                loyalty_id,
                name,
                cost,
                quantity,
                len(modgrps or []),
                _json.dumps(modgrps, ensure_ascii=False)[:1000],
            )
        except Exception:
            pass

        if not loyalty_id:
            return error_response(
                ErrorCode.VALIDATION_ERROR,
                message="loyalty_id est requis",
                http_status=400,
            )

        cost_int = int(cost)
        quantity_int = int(quantity)
        cost_total = cost_int * quantity_int
        new_balance_basket = session.balance_basket + cost_total

        # Limite max de points pour le panier Click&Collect : 2500 points
        MAX_BASKET_POINTS = 2500
        if new_balance_basket > MAX_BASKET_POINTS:
            return error_response(
                ErrorCode.INSUFFICIENT_POINTS,
                message="Limite de points atteinte pour le panier Click & Collect",
                details={
                    "balance_user": session.balance_user,
                    "balance_basket": session.balance_basket,
                    "cost": cost_total,
                    "required": new_balance_basket,
                    "max_basket_points": MAX_BASKET_POINTS,
                },
                http_status=400,
            )

        if new_balance_basket > session.balance_user:
            return error_response(
                ErrorCode.INSUFFICIENT_POINTS,
                message="Points insuffisants",
                details={
                    "balance_user": session.balance_user,
                    "balance_basket": session.balance_basket,
                    "cost": cost_total,
                    "required": new_balance_basket,
                },
                http_status=400,
            )

        try:
            from ressource import basket
            from services.basket_service import add_item_to_session
            from services.session_service import update_session
        except ImportError as e:
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Module indisponible",
                details={"detail": str(e)},
                http_status=502,
            )

        result = basket.AddLoyaltyItemToBasket(
            session.basket_id,
            loyalty_id,
            cost,
            quantity,
            modgrps,
        )
        try:
            import json as _json
            app.logger.info(
                "KFC AddLoyaltyItem result=%s",
                _json.dumps(result, ensure_ascii=False)[:1500],
            )
        except Exception:
            pass
        if result is None:
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Impossible d'ajouter l'article au panier",
                http_status=502,
            )

        # Extraire item_uuid de la réponse KFC pour session_items
        item_uuid = None
        if isinstance(result, dict):
            items = result.get("items", [])
            if isinstance(items, list) and items:
                last_item = items[-1]
                item_uuid = last_item.get("id") or last_item.get("itemId")

        if item_uuid:
            add_item_to_session(
                session_id=session.id,
                item_uuid=str(item_uuid),
                loyalty_id=loyalty_id,
                name=name,
                cost=cost_int,
                quantity=quantity_int,
                modgrps=modgrps,
            )
            update_session(panier_id, balance_basket=new_balance_basket)

        return success_response(result, http_status=201)

    @app.route("/sessions/<panier_id>/basket/items/<item_id>", methods=["DELETE"])
    @handle_api_errors
    def delete_basket_item(panier_id, item_id):
        """DELETE /sessions/<panier_id>/basket/items/<item_id> - Supprimer un article."""
        session, err = _require_session(panier_id)
        if err:
            return err

        if session.status != "DRAFT":
            return error_response(
                ErrorCode.INVALID_STATE,
                message="Seules les sessions DRAFT permettent de supprimer des articles",
                details={"current_status": session.status},
                http_status=400,
            )

        if not session.basket_id:
            return error_response(
                ErrorCode.INVALID_STATE,
                message="Aucun panier associé à cette session",
                http_status=400,
            )

        try:
            from ressource import basket
            from services.basket_service import (
                remove_item_from_session,
                get_item_cost_quantity,
            )
            from services.session_service import update_session
        except ImportError:
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Module indisponible",
                http_status=502,
            )

        item_info = get_item_cost_quantity(session.id, item_id)
        cost_to_remove = (item_info[0] * item_info[1]) if item_info else 0

        result = basket.RemoveLoyaltyItemFromBasket(session.basket_id, item_id)
        if result is None:
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Impossible de supprimer l'article du panier",
                http_status=502,
            )

        remove_item_from_session(session.id, item_id)
        new_balance_basket = max(0, session.balance_basket - cost_to_remove)
        update_session(panier_id, balance_basket=new_balance_basket)

        return success_response({"deleted": True})

    @app.route("/sessions/<panier_id>/checkout", methods=["POST"])
    @handle_api_errors
    def post_checkout(panier_id):
        """POST /sessions/<panier_id>/checkout - Checkout du panier (DRAFT → CHECKOUT)."""
        session, err = _require_session(panier_id)
        if err:
            return err

        if session.status != "DRAFT":
            return error_response(
                ErrorCode.INVALID_STATE,
                message="Le checkout n'est possible qu'en statut DRAFT",
                details={"current_status": session.status},
                http_status=400,
            )

        if not session.basket_id:
            return error_response(
                ErrorCode.INVALID_STATE,
                message="Aucun panier associé à cette session",
                http_status=400,
            )

        try:
            from ressource import order
        except ImportError:
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Module KFC indisponible",
                http_status=502,
            )

        result = order.CheckoutBasket(session.basket_id, session.account_token)
        if result is None:
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Échec du checkout",
                http_status=502,
            )

        update_session(panier_id, status="CHECKOUT")
        return success_response({"status": "CHECKOUT"})

    @app.route("/sessions/<panier_id>/submit", methods=["POST"])
    @handle_api_errors
    def post_submit(panier_id):
        """POST /sessions/<panier_id>/submit - Soumettre la commande (CHECKOUT → SUBMITTED)."""
        session, err = _require_session(panier_id)
        if err:
            return err

        if session.status != "CHECKOUT":
            return error_response(
                ErrorCode.INVALID_STATE,
                message="La soumission n'est possible qu'après checkout (statut CHECKOUT)",
                details={"current_status": session.status},
                http_status=400,
            )

        if not session.basket_id:
            return error_response(
                ErrorCode.INVALID_STATE,
                message="Aucun panier associé à cette session",
                http_status=400,
            )

        try:
            from ressource import order, basket
            from ressource.account import GetUserInfo
        except ImportError:
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Module KFC indisponible",
                http_status=502,
            )

        # Récupérer les infos utilisateur KFC (id, token) et les stocker en session
        user_info = GetUserInfo(session.account_id, session.account_token)
        if user_info:
            date_of_birth = user_info.get("dateOfBirth") or user_info.get("date_of_birth")
            update_session(
                panier_id,
                email=user_info.get("email"),
                phone_number=user_info.get("phoneNumber") or user_info.get("phone_number"),
                last_name=user_info.get("lastName") or user_info.get("last_name"),
                first_name=user_info.get("firstName") or user_info.get("first_name"),
                date_of_birth=date_of_birth,
            )

        # Récupérer les articles du panier pour SubmitOrder
        basket_data = basket.GetBasketById(session.basket_id)
        if basket_data is None:
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Impossible de récupérer le panier",
                http_status=502,
            )

        basket_items = []
        for item in basket_data.get("items", []):
            name = item.get("name") or item.get("productName") or item.get("product", {}).get("name", "")
            qty = item.get("quantity", 1)
            basket_items.append({"name": str(name), "quantity": int(qty)})

        order_uuid, order_number = order.SubmitOrder(
            session.basket_id,
            basket_items,
            session.account_id,
            session.account_token,
            user_info=user_info,
        )

        if order_uuid is None:
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Échec de la soumission (reCAPTCHA ou API KFC)",
                http_status=502,
            )

        update_session(
            panier_id,
            order_uuid=order_uuid,
            order_number=order_number,
            status="SUBMITTED",
        )
        history_id = save_click_order_history_snapshot(panier_id)
        if history_id is None:
            app.logger.warning("Snapshot historique click non créé pour panier_id=%s", panier_id)

        # Recharger la session pour inclure les données utilisateur stockées
        session = get_session(panier_id)
        payload = {
            "order_uuid": order_uuid,
            "order_number": order_number,
            "status": "SUBMITTED",
            "confirmation_url": f"https://kfc.fr/confirmation-de-commande/{order_uuid}",
            "history_id": history_id,
        }
        if session:
            payload["email"] = session.email
            payload["phone_number"] = session.phone_number
            payload["last_name"] = session.last_name
            payload["first_name"] = session.first_name
            payload["date_of_birth"] = session.date_of_birth.isoformat() if session.date_of_birth else None
            payload["store_name"] = session.store_name
            payload["store_city"] = session.store_city
        return success_response(payload)

    @app.route("/sessions/<panier_id>/checkin", methods=["POST"])
    @handle_api_errors
    def post_checkin(panier_id):
        """POST /sessions/<panier_id>/checkin - Check-in (SUBMITTED → CHECKED_IN)."""
        session, err = _require_session(panier_id)
        if err:
            return err

        if session.status != "SUBMITTED":
            return error_response(
                ErrorCode.INVALID_STATE,
                message="Le check-in n'est possible qu'après soumission (statut SUBMITTED)",
                details={"current_status": session.status},
                http_status=400,
            )

        if not session.order_uuid:
            return error_response(
                ErrorCode.INVALID_STATE,
                message="Aucune commande soumise pour cette session",
                http_status=400,
            )

        try:
            from ressource import order
        except ImportError:
            return error_response(
                ErrorCode.KFC_API_ERROR,
                message="Module KFC indisponible",
                http_status=502,
            )

        result = order.CheckinOrder(session.order_uuid, session.account_token)
        if result is None:
            return error_response(
                ErrorCode.CHECKIN_NOT_POSSIBLE,
                message="Le check-in n'est pas possible (trop tôt ou erreur API)",
                http_status=400,
            )

        update_session(panier_id, status="CHECKED_IN")
        updated_rows = update_click_order_history_status(session.order_uuid, "CHECKED_IN")
        if updated_rows == 0:
            app.logger.info("Aucun historique click à mettre à jour pour order_uuid=%s", session.order_uuid)

        return success_response({
            "status": "CHECKED_IN",
            "order_number": session.order_number,
        })

    @app.route("/sessions/<panier_id>", methods=["DELETE"])
    @handle_api_errors
    def delete_sessions(panier_id):
        """DELETE /sessions/<panier_id> - Annuler une session."""
        session, err = _require_session(panier_id)
        if err:
            return err

        if session.status != "DRAFT":
            return error_response(
                ErrorCode.INVALID_STATE,
                message="Seules les sessions DRAFT peuvent être annulées",
                details={"current_status": session.status},
                http_status=400,
            )

        deleted = delete_session(panier_id)
        if not deleted:
            return error_response(
                ErrorCode.INTERNAL_ERROR,
                message="Erreur lors de la suppression",
                http_status=500,
            )

        return success_response({"deleted": True}, http_status=200)
