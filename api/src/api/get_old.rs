use tokio::sync::Mutex;

#[derive(serde::Deserialize)]
struct GetOldRequest {
    pub min_hour_back: i32,
    pub max_results: i64,
    pub already_sold: bool,
}
const MAX_RESULTS_LIMIT: i64 = 1000;
#[actix_web::post("/old")]
pub async fn get_old_kfc(
    req: actix_web::web::Json<GetOldRequest>,
    connection: actix_web::web::Data<std::sync::Arc<Mutex<diesel::PgConnection>>>,
) -> actix_web::HttpResponse {
    let max = req.max_results;
    if max <= 0 {
        return actix_web::HttpResponse::BadRequest().body("max_results must be greater than 0");
    }
    if max > MAX_RESULTS_LIMIT {
        return actix_web::HttpResponse::BadRequest()
            .body("max_results must be less than or equal to 1000");
    }
    let mut connection = connection.lock().await;
    let account = crate::database::get_old_kfc_accounts(
        &mut connection,
        req.min_hour_back as i64,
        max,
        req.already_sold,
    )
    .await;
    match account {
        Ok(kfc_accounts) => actix_web::HttpResponse::Ok().json(kfc_accounts),
        Err(e) => {
            log::error!("Failed to get old KFC account: {}", e);
            actix_web::HttpResponse::InternalServerError().body("Failed to get old KFC account")
        }
    }
}
