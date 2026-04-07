use tokio::sync::Mutex;

use crate::recheck::recheck_kfc_accounts;

#[derive(serde::Deserialize)]
struct MajRequest {
    pub min_hour_back: i32,
    pub max_ligne: i64,
    pub already_sold: bool,
}

#[derive(serde::Serialize)]
struct MajResponse {
    pub updated: u32,
    pub errors: u32,
}

const MAX_LIGNE_LIMIT: i64 = 1000;

#[actix_web::post("/maj")]
pub async fn maj_kfc(
    req: actix_web::web::Json<MajRequest>,
    db_pool: actix_web::web::Data<std::sync::Arc<Mutex<diesel::PgConnection>>>,
) -> actix_web::HttpResponse {
    let max = req.max_ligne;
    if max <= 0 {
        return actix_web::HttpResponse::BadRequest().body("max_ligne must be greater than 0");
    }
    if max > MAX_LIGNE_LIMIT {
        return actix_web::HttpResponse::BadRequest()
            .body("max_ligne must be less than or equal to 1000");
    }

    let rows = {
        let mut conn = db_pool.lock().await;
        match crate::database::get_old_kfc_accounts(
            &mut conn,
            req.min_hour_back as i64,
            max,
            req.already_sold,
        )
        .await
        {
            Ok(r) => r,
            Err(e) => {
                log::error!("maj: get_old_kfc_accounts: {}", e);
                return actix_web::HttpResponse::InternalServerError()
                    .body("Failed to load kfc_storage rows");
            }
        }
    };

    let mut updated: u32 = 0;
    let mut errors: u32 = 0;

    for acc in rows {
        let Some(id) = acc
            .id
            .as_deref()
            .map(str::trim)
            .filter(|s| !s.is_empty())
        else {
            errors += 1;
            continue;
        };

        let token = acc.bearer_token.as_deref().map(str::trim).unwrap_or("");
        if token.is_empty() {
            errors += 1;
            continue;
        }

        let recheck = recheck_kfc_accounts(id, Some(token)).await;
        match recheck {
            Ok(resp) => {
                if resp.customer_id.as_deref() != Some(acc.customer_id.as_str()) {
                    log::warn!(
                        "maj: customerId mismatch for customer_id={}",
                        acc.customer_id
                    );
                    errors += 1;
                    continue;
                }
                let mut conn = db_pool.lock().await;
                match crate::database::update_kfc_point_only(
                    &mut conn,
                    &acc.customer_id,
                    resp.loyalty_points,
                )
                .await
                {
                    Ok(0) => {
                        log::warn!("maj: no row updated for customer_id={}", acc.customer_id);
                        errors += 1;
                    }
                    Ok(_) => updated += 1,
                    Err(e) => {
                        log::error!(
                            "maj: update point failed for customer_id={}: {}",
                            acc.customer_id,
                            e
                        );
                        errors += 1;
                    }
                }
            }
            Err(e) => {
                log::warn!(
                    "maj: recheck failed for customer_id={}: {}",
                    acc.customer_id,
                    e
                );
                errors += 1;
            }
        }
    }

    actix_web::HttpResponse::Ok().json(MajResponse { updated, errors })
}
