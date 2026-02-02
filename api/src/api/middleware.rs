use actix_web::Error;
use actix_web::dev::{Service, ServiceRequest, ServiceResponse, Transform};
use futures::Future;
use futures::future::{Ready, ok};
use lazy_static::lazy_static;
use std::env;
use std::pin::Pin;
use std::rc::Rc;
use std::task::{Context, Poll};

lazy_static! {
    static ref BASIC_AUTH_CREDENTIALS: Option<(String, String)> = {
        match (env::var("BASIC_AUTH_USER"), env::var("BASIC_AUTH_PASSWORD")) {
            (Ok(user), Ok(pass)) => Some((user, pass)),
            _ => None,
        }
    };
}

pub struct BasicAuth;

impl<S, B> Transform<S, ServiceRequest> for BasicAuth
where
    S: Service<ServiceRequest, Response = ServiceResponse<B>, Error = Error> + 'static,
    S::Future: 'static,
    B: 'static,
{
    type Response = ServiceResponse<B>;
    type Error = Error;
    type Transform = BasicAuthMiddleware<S>;
    type InitError = ();
    type Future = Ready<Result<Self::Transform, Self::InitError>>;

    fn new_transform(&self, service: S) -> Self::Future {
        ok(BasicAuthMiddleware {
            service: Rc::new(service),
        })
    }
}

pub struct BasicAuthMiddleware<S> {
    service: Rc<S>,
}

impl<S, B> Service<ServiceRequest> for BasicAuthMiddleware<S>
where
    S: Service<ServiceRequest, Response = ServiceResponse<B>, Error = Error> + 'static,
    S::Future: 'static,
    B: 'static,
{
    type Response = ServiceResponse<B>;
    type Error = Error;
    type Future = Pin<Box<dyn Future<Output = Result<Self::Response, Self::Error>>>>;

    fn poll_ready(&self, ctx: &mut Context<'_>) -> Poll<Result<(), Self::Error>> {
        self.service.poll_ready(ctx)
    }

    fn call(&self, req: ServiceRequest) -> Self::Future {
        let srv = self.service.clone();

        Box::pin(async move {
            if let Some((expected_user, expected_pass)) = &*BASIC_AUTH_CREDENTIALS {
                if let Some(auth_header) = req.headers().get("Authorization") {
                    if let Ok(auth_str) = auth_header.to_str() {
                        if auth_str.starts_with("Basic ") {
                            let token = &auth_str[6..];
                            if let Ok(decoded) = base64::decode(token) {
                                if let Ok(credentials) = String::from_utf8(decoded) {
                                    let parts: Vec<&str> = credentials.splitn(2, ':').collect();
                                    if parts.len() == 2 {
                                        let user = parts[0];
                                        let pass = parts[1];

                                        if user == expected_user && pass == expected_pass {
                                            return srv.call(req).await;
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                return Err(actix_web::error::ErrorUnauthorized("Unauthorized"));
            }
            Err(actix_web::error::ErrorUnauthorized(
                "Server configuration error: Missing auth credentials",
            ))
        })
    }
}
