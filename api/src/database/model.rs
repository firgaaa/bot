use diesel::{
    BoolExpressionMethods, ExpressionMethods, RunQueryDsl, Selectable, SelectableHelper,
    prelude::{AsChangeset, Insertable, Queryable, QueryableByName},
    query_dsl::methods::{FilterDsl, LimitDsl, SelectDsl},
};

use crate::{errors::AppError, recheck::recheck_kfc_accounts, schema::kfc_storage};

#[derive(Queryable, Insertable, serde::Serialize, serde::Deserialize)]
#[diesel(table_name = kfc_storage)]
pub struct AddKfcStorage {
    id: Option<String>,
    customer_id: String,   // requis
    carte: String,
    email: Option<String>,
    password: Option<String>,
    nom: Option<String>,
    point: i32,
    expired_at: Option<chrono::NaiveDateTime>,
    prenom: Option<String>,
    numero: Option<String>,
    ddb: Option<String>,   // chaîne stockée telle quelle, ex: "1992-07-26T00:00:00.000Z"
}

#[derive(serde::Serialize, serde::Deserialize)]
pub struct UpdateKfcStorage {
    pub customer_id: String,
    pub id: Option<String>,
    pub carte: Option<String>,
    pub email: Option<String>,
    pub password: Option<String>,
    pub nom: Option<String>,
    pub point: Option<i32>,
    pub expired_at: Option<chrono::NaiveDateTime>,
    pub prenom: Option<String>,
    pub numero: Option<String>,
    pub ddb: Option<String>,
}

#[derive(AsChangeset)]
#[diesel(table_name = kfc_storage)]
pub struct UpdateKfcStorageSet {
    pub id: Option<String>,
    pub carte: Option<String>,
    pub email: Option<String>,
    pub password: Option<String>,
    pub nom: Option<String>,
    pub point: Option<i32>,
    pub expired_at: Option<chrono::NaiveDateTime>,
    pub prenom: Option<String>,
    pub numero: Option<String>,
    pub ddb: Option<String>,
}
#[derive(serde::Serialize, serde::Deserialize, Queryable, Selectable, QueryableByName, Clone)]
#[diesel(table_name = kfc_storage)]
pub struct Kfc {
    #[serde(rename = "customerId")]
    customer_id: String,
    id: Option<String>,
    carte: String,
    point: Option<i32>,
    expired_at: Option<chrono::NaiveDateTime>,
    prenom: Option<String>,
    numero: Option<String>,
    ddb: Option<String>,
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
            .filter(id.is_not_null()) // filter out accounts that have no id
            .limit(10)
            .load(connection)?;
        // mark all as sold
        if acccounts.is_empty() {
            return diesel::result::QueryResult::Ok(None);
        }
        for acc in &acccounts {
            diesel::update(kfc_storage.filter(customer_id.eq(&acc.customer_id)))
                .set(deja_send.eq(true))
                .execute(connection)?;
        }
        diesel::result::QueryResult::Ok(Some(acccounts))
    })?;

    let mut result: Option<Kfc> = None;
    if let Some(accounts) = accounts {
        for mut acc in accounts.clone() {
            // recheck each account
            let response = match acc.id.as_ref() {
                Some(acc_id) => recheck_kfc_accounts(acc_id).await,
                None => continue,  // ne devrait pas arriver grâce au filter id.is_not_null()
            };
            match response {
                Ok(kfc_response) => {
                    log::debug!(
                        "KFC account {} is valid during generation with {} points.",
                        acc.id.as_deref().unwrap_or("N/A"),
                        kfc_response.loyalty_points
                    );
                    if kfc_response.customer_id.as_deref() != Some(acc.customer_id.as_str()) {
                        // null OU différent → rejeter (marquer expiré, etc.)
                        log::warn!("KFC account {} invalid: customerId null or mismatch", acc.customer_id);
                        let _ = diesel::update(kfc_storage.filter(customer_id.eq(&acc.customer_id)))
                            .set(status.eq("expired"))
                            .execute(conn);
                        continue;
                    }
                    if kfc_response.loyalty_points < min_points
                        || kfc_response.loyalty_points > max_points
                    {
                        log::warn!(
                            "KFC account {} has {} points which is out of range during generation.",
                            acc.id.as_deref().unwrap_or("N/A"),
                            kfc_response.loyalty_points
                        );
                        // remark as not sold
                        let _ = diesel::update(kfc_storage.filter(customer_id.eq(&acc.customer_id)))
                            .set((deja_send.eq(false), point.eq(kfc_response.loyalty_points)))
                            .execute(conn);
                        continue;
                    }
                    acc.point = Some(kfc_response.loyalty_points);
                    result = Some(acc);
                    break;
                }
                Err(e) => {
                    log::warn!("KFC account {} is invalid during generation: {}", acc.id.as_deref().unwrap_or("N/A"), e);
                    // remark as not sold
                    let _ = diesel::update(kfc_storage.filter(customer_id.eq(&acc.customer_id)))
                        .set(deja_send.eq(false))
                        .execute(conn);
                }
            }
        }
        // for each account not selected, remark as not sold
        for acc in accounts {
            if let Some(ref res) = result {
                if acc.customer_id != res.customer_id {
                    let _ = diesel::update(kfc_storage.filter(customer_id.eq(&acc.customer_id)))
                        .set(deja_send.eq(false))
                        .execute(conn);
                }
            } else {
                let _ = diesel::update(kfc_storage.filter(customer_id.eq(&acc.customer_id)))
                    .set(deja_send.eq(false))
                    .execute(conn);
            }
        }
    }
    Ok(result)
}
