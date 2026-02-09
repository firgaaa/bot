// @generated automatically by Diesel CLI.

diesel::table! {
    card_purchase_history (id) {
        id -> Int4,
        user_id -> Int8,
        #[max_length = 255]
        card_number -> Varchar,
        points -> Int4,
        created_at -> Timestamp,
    }
}

diesel::table! {
    config (key) {
        #[max_length = 255]
        key -> Varchar,
        value -> Text,
        updated_at -> Timestamp,
    }
}

diesel::table! {
    kfc_storage (customer_id) {
        #[max_length = 255]
        id -> Nullable<Varchar>,
        created_at -> Nullable<Timestamp>,
        updated_at -> Nullable<Timestamp>,
        #[max_length = 6]
        carte -> Varchar,
        deja_send -> Nullable<Bool>,
        #[max_length = 50]
        status -> Nullable<Varchar>,
        #[max_length = 255]
        customer_id -> Varchar,
        #[max_length = 255]
        email -> Nullable<Varchar>,
        #[max_length = 255]
        password -> Nullable<Varchar>,
        #[max_length = 255]
        nom -> Nullable<Varchar>,
        point -> Nullable<Int4>,
        expired_at -> Nullable<Timestamp>,
        #[max_length = 255]
        prenom -> Nullable<Varchar>,
        #[max_length = 20]
        numero -> Nullable<Varchar>,
        #[max_length = 50]
        ddb -> Nullable<Varchar>,
    }
}

diesel::table! {
    pending_payments (id) {
        id -> Int4,
        user_id -> Int8,
        points -> Int4,
        price -> Numeric,
        photo_file_id -> Nullable<Text>,
        created_at -> Timestamp,
        #[max_length = 50]
        status -> Varchar,
        confirmation_message_id -> Nullable<Int4>,
    }
}

diesel::table! {
    users (user_id) {
        user_id -> Int8,
        balance -> Int4,
        #[max_length = 50]
        role -> Nullable<Varchar>,
        created_at -> Timestamp,
        updated_at -> Timestamp,
        #[max_length = 255]
        username -> Nullable<Varchar>,
        reduction -> Nullable<Int4>,
        #[max_length = 64]
        token_publique -> Nullable<Varchar>,
    }
}

diesel::joinable!(card_purchase_history -> users (user_id));
diesel::joinable!(pending_payments -> users (user_id));

diesel::allow_tables_to_appear_in_same_query!(
    card_purchase_history,
    config,
    kfc_storage,
    pending_payments,
    users,
);
