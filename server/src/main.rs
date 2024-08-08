use actix_web::{web::Data, App, HttpServer};

use server::{server::search, State};

use std::sync::{Arc, Mutex};

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let data = Data::new(Mutex::new(State::new(true).unwrap()));
    HttpServer::new(move || App::new().app_data(Data::clone(&data)).service(search))
        .bind(("127.0.0.1", 8080))?
        .run()
        .await
}
