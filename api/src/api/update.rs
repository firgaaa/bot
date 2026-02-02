#[actix_web::put("/update")]
pub async fn update_kfc_account(
    db_pool: actix_web::web::Data<std::sync::Arc<tokio::sync::Mutex<diesel::PgConnection>>>,
    updated_account: actix_web::web::Json<crate::database::model::UpdateKfcStorage>,
) -> actix_web::HttpResponse {
    let mut conn = db_pool.lock().await;
    let updated_account = updated_account.into_inner();
    match crate::database::update_kfc_account(&mut conn, updated_account).await {
        Ok(_) => actix_web::HttpResponse::NoContent().finish(),
        Err(e) => {
            if e == diesel::result::Error::NotFound {
                return actix_web::HttpResponse::NotFound().body("KFC account not found");
            }
            log::error!("Failed to update KFC account: {}", e);
            actix_web::HttpResponse::InternalServerError().body("Failed to update KFC account")
        }
    }
}
