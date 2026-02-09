use diesel::{
    Connection, ConnectionError, ExpressionMethods, RunQueryDsl, SelectableHelper,
    query_dsl::methods::{FilterDsl, LimitDsl, SelectDsl},
};
pub mod model;
pub async fn establish_connection() -> Result<diesel::PgConnection, ConnectionError> {
    let database_url =
        std::env::var("DATABASE_URL").expect("DATABASE_URL must be set in environment variables");
    let pool = diesel::PgConnection::establish(&database_url)?;
    Ok(pool)
}

pub async fn insert_kfc_account(
    conn: &mut diesel::PgConnection,
    kfc_account: model::AddKfcStorage,
) -> Result<(), diesel::result::Error> {
    use crate::schema::kfc_storage;
    diesel::insert_into(kfc_storage::table)
        .values(&kfc_account)
        .execute(conn)?;
    Ok(())
}

pub async fn update_kfc_account(
    conn: &mut diesel::PgConnection,
    kfc_account: model::UpdateKfcStorage,
) -> Result<(), diesel::result::Error> {
    use crate::schema::kfc_storage::dsl::*;
    let set = model::UpdateKfcStorageSet {
        id: kfc_account.id,
        carte: kfc_account.carte,
        email: kfc_account.email,
        password: kfc_account.password,
        nom: kfc_account.nom,
        point: kfc_account.point,
        expired_at: kfc_account.expired_at,
        prenom: kfc_account.prenom,
        numero: kfc_account.numero,
        ddb: kfc_account.ddb,
    };
    diesel::update(kfc_storage.filter(customer_id.eq(&kfc_account.customer_id)))
        .set(&set)
        .execute(conn)?;
    Ok(())
}

pub async fn get_old_kfc_accounts(
    conn: &mut diesel::PgConnection,
    min_hours: i64,
    limit_count: i64,
    already_sold: bool,
) -> Result<Vec<model::Kfc>, diesel::result::Error> {
    use crate::schema::kfc_storage::dsl::*;
    use chrono::Utc;
    let cutoff_time = Utc::now().naive_utc() - chrono::Duration::hours(min_hours);
    let results = kfc_storage
        .select(model::Kfc::as_select())
        .filter(deja_send.eq(already_sold))
        .filter(updated_at.ge(cutoff_time))
        .limit(limit_count)
        .load::<model::Kfc>(conn)?;
    Ok(results)
}
