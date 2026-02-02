use diesel::PgConnection;
use tokio::sync::Mutex;

use crate::database::model::generate_kfc_storage;

#[derive(serde::Deserialize)]
struct GenerateRequest {
    pub min_points: i32,
    pub max_points: i32,
}

#[actix_web::post("/generate")]
pub async fn generate_kfc(
    req: actix_web::web::Json<GenerateRequest>,
    connection: actix_web::web::Data<std::sync::Arc<Mutex<PgConnection>>>,
) -> actix_web::HttpResponse {
    if req.min_points > req.max_points {
        return actix_web::HttpResponse::BadRequest()
            .body("min_points cannot be greater than max_points");
    }
    let mut connection = connection.lock().await;
    let account = generate_kfc_storage(&mut connection, req.min_points, req.max_points);
    match account.await {
        Ok(Some(kfc_account)) => actix_web::HttpResponse::Ok().json(kfc_account),
        Ok(None) => actix_web::HttpResponse::NotFound()
            .body("No KFC account found in the specified point range"),
        Err(e) => {
            log::error!("Failed to generate KFC account: {}", e);
            actix_web::HttpResponse::InternalServerError().body("Failed to generate KFC account")
        }
    }
}
