use crate::errors::AppError;

#[derive(Debug, serde::Serialize, serde::Deserialize, Default)]
pub struct KfcResponse {
    #[serde(rename = "customerId")]
    pub customer_id: Option<String>,
    pub id: String,
    #[serde(rename = "loyaltyPoints")]
    pub loyalty_points: i32,
    #[serde(rename = "pointExpireDate")]
    point_expire_date: String,
}

pub async fn recheck_kfc_accounts(id: &str, bearer_token: Option<&str>) -> Result<KfcResponse, AppError> {
    let client = wreq::Client::builder()
        .timeout(std::time::Duration::from_secs(10))
        .emulation(wreq_util::Emulation::random())
        .cert_verification(false)
        .build()
        .unwrap();
    let url = format!("https://13.248.197.133/api/users/{}/loyaltyinfo", id);
    log::debug!("Rechecking KFC account with URL: {}", &url);
    let token = bearer_token.unwrap_or("").trim();
    if token.is_empty() {
        return Err(AppError::RecheckError("bearer token manquant".into()));
    }
    let resp = client
        .get(&url)
        .header("Authorization", format!("Bearer {}", token))
        .send()
        .await;
    match resp {
        Ok(response) => {
            let status = response.status();
            let body = response.text().await.unwrap_or_default();

            // Cas token invalide/expiré (API renvoie souvent {"title":"Unauthorized", ...})
            if let Ok(v) = serde_json::from_str::<serde_json::Value>(&body) {
                if v.get("title")
                    .and_then(|t| t.as_str())
                    .is_some_and(|t| t.eq_ignore_ascii_case("Unauthorized"))
                {
                    log::warn!("KFC bearer token unauthorized for id={}", id);
                    return Err(AppError::RecheckError("bearer token invalide/unauthorized".into()));
                }
            }

            if status.is_success() {
                log::info!("KFC account {} is valid.", id);
                match serde_json::from_str::<KfcResponse>(&body) {
                    Ok(kfc_response) => Ok(kfc_response),
                    Err(e) => {
                        log::error!("Failed to parse KFC account {} response: {}", id, e);
                        return Err(AppError::RecheckError(
                            "Failed to parse KFC account response".into(),
                        ));
                    }
                }
            } else {
                log::warn!(
                    "KFC account {} is invalid. Status: {}",
                    id,
                    status
                );
                Err(AppError::RecheckError("KFC account is invalid".into()))
            }
        }
        Err(e) => {
            log::error!("Error checking KFC account {}: {}", id, e);
            Err(AppError::RecheckError("Error checking KFC account".into()))
        }
    }
}
