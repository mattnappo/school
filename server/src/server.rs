use super::model;
use super::*;
use actix_web::{get, web, Responder};
use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};

#[derive(Deserialize)]
struct Search {
    q: String,
}

#[derive(Serialize)]
struct SearchResponse {
    metadata: String,
    pubs: Vec<model::Publication>,
}

#[get("/search")]
async fn search(
    state: web::Data<Mutex<State>>,
    req: web::Query<Search>,
) -> std::io::Result<impl Responder> {
    let t0 = std::time::Instant::now();

    // can try using actix_web::Result;
    let mut s = state.lock().unwrap();
    let pubs = s
        .search(&req.q)
        .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e.to_string()))?;

    let metadata = format!(
        "found {} results in {} ms",
        pubs.len(),
        (std::time::Instant::now() - t0).as_millis()
    );
    println!("{metadata}");

    Ok(web::Json(SearchResponse { metadata, pubs }))
}
