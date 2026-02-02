use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("Database error: {0}")]
    DatabaseError(#[from] diesel::result::Error),
    #[error("KFC account not found")]
    _NotFound,
    #[error("HTTP request error: {0}")]
    HttpRequestError(#[from] wreq::Error),
    #[error("Invalid KFC account")]
    _InvalidAccount,
    #[error("Unknown error")]
    _Unknown,
    #[error("Kfc recheck error: {0}")]
    RecheckError(String),
    #[error("Kfc account have bad points")]
    _BadPoints,
}
