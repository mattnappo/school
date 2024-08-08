use super::*;
use actix_web::{get, web, Responder};
use serde::Deserialize;
use std::sync::{Arc, Mutex};

#[derive(Deserialize)]
struct Search {
    q: String,
}

struct Data {
    state: State,
}

#[get("/search")]
async fn search(state: web::Data<Mutex<State>>, req: web::Query<Search>) -> impl Responder {
    let t0 = std::time::Instant::now();

    let mut s = state.lock().unwrap();
    let res = s.search(&req.q).unwrap();

    println!(
        "found {} results in {} ns",
        res.len(),
        (std::time::Instant::now() - t0).as_nanos()
    );

    format!("{res:#?}")
}
