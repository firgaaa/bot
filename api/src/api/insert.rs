use tokio::sync::Mutex;

#[actix_web::post("/insert")]
pub async fn insert_kfc_account(
    db_pool: actix_web::web::Data<std::sync::Arc<Mutex<diesel::PgConnection>>>,
    new_account: actix_web::web::Json<crate::database::model::AddKfcStorage>,
) -> actix_web::HttpResponse {
    let mut conn = db_pool.lock().await;
    let new_account = new_account.into_inner();
    match crate::database::insert_kfc_account(&mut conn, new_account).await {
        Ok(_) => actix_web::HttpResponse::NoContent().finish(),
        Err(e) => {
            log::error!("Failed to insert KFC account: {}", e);
            actix_web::HttpResponse::InternalServerError().body("Failed to insert KFC account")
        }
    }
}
