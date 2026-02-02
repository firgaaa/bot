use crate::errors::AppError;

#[derive(Debug, serde::Serialize, serde::Deserialize, Default)]
pub struct KfcResponse {
    #[serde(rename = "customerId")]
    pub customer_id: String,
    pub id: String,
    #[serde(rename = "loyaltyPoints")]
    pub loyalty_points: i32,
    #[serde(rename = "pointExpireDate")]
    point_expire_date: String,
}

pub async fn recheck_kfc_accounts(id: &str) -> Result<KfcResponse, AppError> {
    let client = wreq::Client::builder()
        .timeout(std::time::Duration::from_secs(5))
        .emulation(wreq_util::Emulation::random())
        .cert_verification(false)
        .build()
        .unwrap();
    let url = format!("https://13.248.197.133/api/users/{}/loyaltyinfo", id);
    log::debug!("Rechecking KFC account with URL: {}", &url);
    let resp = client.get(&url).send().await;
    match resp {
        Ok(response) => {
            if response.status().is_success() {
                log::info!("KFC account {} is valid.", id);
                match response.json::<KfcResponse>().await {
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
                    response.status()
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
