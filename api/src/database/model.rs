use diesel::{
    BoolExpressionMethods, ExpressionMethods, RunQueryDsl, Selectable, SelectableHelper,
    prelude::{AsChangeset, Insertable, Queryable, QueryableByName},
    query_dsl::methods::{FilterDsl, LimitDsl, SelectDsl},
};

use crate::{errors::AppError, recheck::recheck_kfc_accounts, schema::kfc_storage};

#[derive(Queryable, Insertable, serde::Serialize, serde::Deserialize)]
#[diesel(table_name = kfc_storage)]
pub struct AddKfcStorage {
    id: String,
    carte: String,
    customer_id: Option<String>,
    email: Option<String>,
    password: Option<String>,
    nom: Option<String>,
    point: i32,
    expired_at: Option<chrono::NaiveDateTime>,
}

#[derive(serde::Serialize, serde::Deserialize, AsChangeset)]
#[diesel(table_name = kfc_storage)]
pub struct UpdateKfcStorage {
    pub id: String,
    pub carte: Option<String>,
    pub customer_id: Option<String>,
    pub email: Option<String>,
    pub password: Option<String>,
    pub nom: Option<String>,
    pub point: Option<i32>,
    pub expired_at: Option<chrono::NaiveDateTime>,
}
#[derive(serde::Serialize, serde::Deserialize, Queryable, Selectable, QueryableByName, Clone)]
#[diesel(table_name = kfc_storage)]
pub struct Kfc {
    id: String,
    #[serde(rename = "customerId")]
    customer_id: Option<String>,
    carte: String,
    point: Option<i32>,
    expired_at: Option<chrono::NaiveDateTime>,
}
pub async fn generate_kfc_storage(
    conn: &mut diesel::PgConnection,
    min_points: i32,
    max_points: i32,
) -> Result<Option<Kfc>, AppError> {
    use crate::schema::kfc_storage::dsl::*;
    // make transaction to select kfc accounts within the point range
    let accounts = diesel::Connection::transaction(conn, |connection| {
        let acccounts = kfc_storage
            .select(Kfc::as_select())
            .filter(point.ge(min_points))
            .filter(point.le(max_points))
            .filter(status.ne("expired"))
            .filter(deja_send.is_null().or(deja_send.eq(false)))
            .limit(10)
            .load(connection)?;
        // mark all as sold
        if acccounts.is_empty() {
            return diesel::result::QueryResult::Ok(None);
        }
        for acc in &acccounts {
            diesel::update(kfc_storage.filter(id.eq(&acc.id)))
                .set(deja_send.eq(true))
                .execute(connection)?;
        }
        diesel::result::QueryResult::Ok(Some(acccounts))
    })?;

    let mut result: Option<Kfc> = None;
    if let Some(accounts) = accounts {
        for mut acc in accounts.clone() {
            // recheck each account
            let response = recheck_kfc_accounts(&acc.id).await;
            match response {
                Ok(kfc_response) => {
                    log::debug!(
                        "KFC account {} is valid during generation with {} points.",
                        acc.id,
                        kfc_response.loyalty_points
                    );
                    if acc.customer_id != Some(kfc_response.customer_id) {
                        log::warn!("KFC account {} has changed id during generation.", acc.id);
                        let _ = diesel::update(kfc_storage.filter(id.eq(&acc.id)))
                            .set(status.eq("expired"))
                            .execute(conn);
                        continue;
                    }
                    if kfc_response.loyalty_points < min_points
                        || kfc_response.loyalty_points > max_points
                    {
                        log::warn!(
                            "KFC account {} has {} points which is out of range during generation.",
                            acc.id,
                            kfc_response.loyalty_points
                        );
                        // remark as not sold
                        let _ = diesel::update(kfc_storage.filter(id.eq(&acc.id)))
                            .set((deja_send.eq(false), point.eq(kfc_response.loyalty_points)))
                            .execute(conn);
                        continue;
                    }
                    acc.point = Some(kfc_response.loyalty_points);
                    result = Some(acc);
                    break;
                }
                Err(e) => {
                    log::warn!("KFC account {} is invalid during generation: {}", acc.id, e);
                    // remark as not sold
                    let _ = diesel::update(kfc_storage.filter(id.eq(&acc.id)))
                        .set(deja_send.eq(false))
                        .execute(conn);
                }
            }
        }
        // for each account not selected, remark as not sold
        for acc in accounts {
            if let Some(ref res) = result {
                if acc.id != res.id {
                    let _ = diesel::update(kfc_storage.filter(id.eq(&acc.id)))
                        .set(deja_send.eq(false))
                        .execute(conn);
                }
            } else {
                let _ = diesel::update(kfc_storage.filter(id.eq(&acc.id)))
                    .set(deja_send.eq(false))
                    .execute(conn);
            }
        }
    }
    Ok(result)
}
