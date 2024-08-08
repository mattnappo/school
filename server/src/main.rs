use std::sync::{Arc, Mutex};

use actix_web::{web::Data, App, HttpServer};
use clap::Parser;

use server::{server::search, State};

#[derive(Parser, Debug)]
struct Args {
    #[arg(short, long, default_value = "0.0.0.0")]
    ip: String,
    #[arg(short, long, default_value_t = 8080)]
    port: u16,
    #[arg(short, long, default_value_t = false)]
    re_index: bool,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let args = Args::parse();

    let data = Data::new(Mutex::new(State::new(args.re_index).unwrap()));
    HttpServer::new(move || App::new().app_data(Data::clone(&data)).service(search))
        .bind((args.ip, args.port))?
        .run()
        .await
}
