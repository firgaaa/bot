// @generated automatically by Diesel CLI.

diesel::table! {
    kfc_storage (id) {
        #[max_length = 255]
        id -> Varchar,
        created_at -> Nullable<Timestamp>,
        updated_at -> Nullable<Timestamp>,
        #[max_length = 6]
        carte -> Varchar,
        deja_send -> Nullable<Bool>,
        #[max_length = 50]
        status -> Nullable<Varchar>,
        #[max_length = 255]
        customer_id -> Nullable<Varchar>,
        #[max_length = 255]
        email -> Nullable<Varchar>,
        #[max_length = 255]
        password -> Nullable<Varchar>,
        #[max_length = 255]
        nom -> Nullable<Varchar>,
        point -> Nullable<Int4>,
        expired_at -> Nullable<Timestamp>,
    }
}
