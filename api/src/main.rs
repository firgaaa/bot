use std::sync::Arc;

use actix_web::web;
use tokio::sync::Mutex;

mod api;
mod database;
mod errors;
mod recheck;
mod schema;
#[actix_web::main]
async fn main() -> std::io::Result<()> {
    dotenv::dotenv().ok();
    env_logger::init();
    log::info!("Starting clemser_kfc_api...");
    log::info!("Loading database configuration...");
    let db_pool = database::establish_connection()
        .await
        .expect("Failed to connect to the database");
    let db_pool = Arc::new(Mutex::new(db_pool));
    log::info!("Database connected successfully.");
    let port = std::env::var("PORT")
        .unwrap_or_else(|_| "8080".to_string())
        .parse::<u16>()
        .expect("PORT must be a valid u16 number");
    let server = actix_web::HttpServer::new(move || {
        actix_web::App::new()
            .wrap(api::middleware::BasicAuth)
            .app_data(web::Data::new(db_pool.clone()))
            .service(api::insert::insert_kfc_account)
            .service(api::update::update_kfc_account)
            .service(api::generate::generate_kfc)
            .service(api::get_old::get_old_kfc)
    });
    log::info!("Starting server on port {}", port);
    server.bind(("0.0.0.0", port))?.run().await
}
