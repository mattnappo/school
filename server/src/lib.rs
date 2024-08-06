use std::fs;
use std::path::Path;
use std::process;
use std::thread;
use std::time;

use anyhow::Result;
use redis;
use serde_json as json;

pub mod model;

const DATA_FILE: &'static str = "../parsed/out.json";

fn restart_redis() -> Result<()> {
    Ok(())
}

struct State {
    rdb: redis::Client,
    conn: redis::Connection,
}

impl State {
    pub fn new(reset_rdb: bool) -> Result<Self> {
        if reset_rdb {
            restart_redis()?;
        }

        let client = redis::Client::open("redis://127.0.0.1/")?;
        let conn = client.get_connection()?;

        let s = State { rdb: client, conn };

        s.init(DATA_FILE)?;

        Ok(s)
    }

    fn init(&self, data_file: impl AsRef<Path>) -> Result<()> {
        let text = fs::read_to_string(data_file)?;
        let data: Vec<json::Value> = json::from_str(&text)?;

        // TODO: remove unwrap
        let profs = data
            .into_iter()
            .map(|item| model::Professor::new(&item).unwrap())
            .collect::<Vec<model::Professor>>();
        println!("{:#?}", profs);

        Ok(())
    }
}

#[cfg(test)]
pub mod tests {
    use super::*;

    #[test]
    fn test_start() -> Result<()> {
        let _state = State::new(false)?;

        Ok(())
    }
}
