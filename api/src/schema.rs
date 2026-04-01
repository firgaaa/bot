// @generated automatically by Diesel CLI.

diesel::table! {
    card_purchase_history (id) {
        id -> Int4,
        user_id -> Int8,
        #[max_length = 255]
        card_number -> Varchar,
        points -> Int4,
        created_at -> Timestamp,
        #[max_length = 255]
        customer_id -> Nullable<Varchar>,
        #[max_length = 255]
        kfc_id -> Nullable<Varchar>,
        expired_at -> Nullable<Timestamp>,
        #[max_length = 255]
        prenom -> Nullable<Varchar>,
        #[max_length = 50]
        numero -> Nullable<Varchar>,
        #[max_length = 50]
        ddb -> Nullable<Varchar>,
    }
}

diesel::table! {
    click_order_history (id) {
        id -> Int4,
        user_id -> Int8,
        #[max_length = 255]
        panier_id -> Varchar,
        session_id -> Nullable<Int4>,
        #[max_length = 255]
        order_uuid -> Nullable<Varchar>,
        #[max_length = 50]
        order_number -> Nullable<Varchar>,
        confirmation_url -> Nullable<Text>,
        #[max_length = 50]
        status -> Varchar,
        #[max_length = 255]
        store_id -> Nullable<Varchar>,
        #[max_length = 255]
        store_name -> Nullable<Varchar>,
        #[max_length = 255]
        store_city -> Nullable<Varchar>,
        #[max_length = 255]
        account_id -> Nullable<Varchar>,
        #[max_length = 255]
        telegram_user -> Nullable<Varchar>,
        #[max_length = 255]
        email -> Nullable<Varchar>,
        #[max_length = 100]
        phone_number -> Nullable<Varchar>,
        #[max_length = 255]
        last_name -> Nullable<Varchar>,
        #[max_length = 255]
        first_name -> Nullable<Varchar>,
        date_of_birth -> Nullable<Date>,
        total_points -> Int4,
        submitted_at -> Timestamptz,
        created_at -> Timestamptz,
    }
}

diesel::table! {
    click_order_history_items (id) {
        id -> Int4,
        history_id -> Int4,
        #[max_length = 255]
        item_uuid -> Nullable<Varchar>,
        #[max_length = 255]
        loyalty_id -> Nullable<Varchar>,
        #[max_length = 255]
        name -> Nullable<Varchar>,
        cost -> Int4,
        quantity -> Int4,
        line_total_points -> Int4,
        modgrps -> Jsonb,
        created_at -> Timestamptz,
    }
}

diesel::table! {
    config (key) {
        #[max_length = 255]
        key -> Varchar,
        value -> Text,
        updated_at -> Timestamp,
    }
}

diesel::table! {
    kfc_storage (customer_id) {
        #[max_length = 255]
        id -> Nullable<Varchar>,
        created_at -> Nullable<Timestamp>,
        updated_at -> Nullable<Timestamp>,
        #[max_length = 6]
        carte -> Varchar,
        deja_send -> Nullable<Bool>,
        #[max_length = 50]
        status -> Nullable<Varchar>,
        #[max_length = 255]
        customer_id -> Varchar,
        #[max_length = 255]
        email -> Nullable<Varchar>,
        #[max_length = 255]
        password -> Nullable<Varchar>,
        #[max_length = 255]
        nom -> Nullable<Varchar>,
        point -> Nullable<Int4>,
        expired_at -> Nullable<Timestamp>,
        #[max_length = 255]
        prenom -> Nullable<Varchar>,
        #[max_length = 20]
        numero -> Nullable<Varchar>,
        #[max_length = 50]
        ddb -> Nullable<Varchar>,
    }
}

diesel::table! {
    nouveau_user (user_id) {
        user_id -> Int8,
        #[max_length = 255]
        username -> Nullable<Varchar>,
        demande_en_attente -> Bool,
        nb_tentatives -> Int4,
        accepte -> Bool,
        last_demande -> Nullable<Timestamp>,
    }
}

diesel::table! {
    pending_payments (id) {
        id -> Int4,
        user_id -> Int8,
        points -> Int4,
        price -> Numeric,
        photo_file_id -> Nullable<Text>,
        created_at -> Timestamp,
        #[max_length = 50]
        status -> Varchar,
        confirmation_message_id -> Nullable<Int4>,
    }
}

diesel::table! {
    session_items (id) {
        id -> Int4,
        session_id -> Int4,
        #[max_length = 255]
        item_uuid -> Varchar,
        #[max_length = 255]
        loyalty_id -> Varchar,
        #[max_length = 255]
        name -> Nullable<Varchar>,
        cost -> Int4,
        quantity -> Int4,
        modgrps -> Nullable<Jsonb>,
        created_at -> Nullable<Timestamptz>,
    }
}

diesel::table! {
    sessions (id) {
        id -> Int4,
        #[max_length = 255]
        account_id -> Varchar,
        account_token -> Text,
        #[max_length = 255]
        store_id -> Varchar,
        #[max_length = 255]
        store_name -> Nullable<Varchar>,
        #[max_length = 255]
        store_city -> Nullable<Varchar>,
        #[max_length = 255]
        basket_id -> Nullable<Varchar>,
        #[max_length = 255]
        order_uuid -> Nullable<Varchar>,
        #[max_length = 50]
        order_number -> Nullable<Varchar>,
        #[max_length = 50]
        status -> Varchar,
        created_at -> Nullable<Timestamptz>,
        updated_at -> Nullable<Timestamptz>,
        balance_user -> Int4,
        balance_basket -> Int4,
        #[max_length = 255]
        telegram_user -> Nullable<Varchar>,
        #[max_length = 255]
        panier_id -> Varchar,
        #[max_length = 255]
        telegram_id -> Nullable<Varchar>,
        #[max_length = 255]
        email -> Nullable<Varchar>,
        #[max_length = 100]
        phone_number -> Nullable<Varchar>,
        #[max_length = 255]
        last_name -> Nullable<Varchar>,
        #[max_length = 255]
        first_name -> Nullable<Varchar>,
        date_of_birth -> Nullable<Date>,
    }
}

diesel::table! {
    users (user_id) {
        user_id -> Int8,
        points -> Int4,
        #[max_length = 50]
        role -> Nullable<Varchar>,
        created_at -> Timestamp,
        updated_at -> Timestamp,
        #[max_length = 255]
        username -> Nullable<Varchar>,
        reduction -> Nullable<Numeric>,
        #[max_length = 64]
        token_publique -> Nullable<Varchar>,
        #[max_length = 64]
        token_prive -> Nullable<Varchar>,
    }
}

diesel::joinable!(card_purchase_history -> users (user_id));
diesel::joinable!(click_order_history_items -> click_order_history (history_id));
diesel::joinable!(pending_payments -> users (user_id));
diesel::joinable!(session_items -> sessions (session_id));

diesel::allow_tables_to_appear_in_same_query!(
    card_purchase_history,
    click_order_history,
    click_order_history_items,
    config,
    kfc_storage,
    nouveau_user,
    pending_payments,
    session_items,
    sessions,
    users,
);
