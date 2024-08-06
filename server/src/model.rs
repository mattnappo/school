use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use serde_json as json;

/*
macro_rules! field {
   ($item:expr, $field:expr) => {
       let $field = $item.get(stringify!($field)).context(concat!("missing field ", stringify!($field)))?.to_string();
   };
}
*/

#[derive(Debug, Serialize, Deserialize)]
pub struct Professor {
    first: String,
    last: String,
    middle: Option<String>,
    website: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Publication {
    author: Professor,
    title: String,
    r#abstract: String,
    url: String,
    pub_year: Option<u64>,
}

impl redis::FromRedisValue for Professor {
    fn from_redis_value(v: &redis::Value) -> redis::RedisResult<Self> {
        //let t = v.into_sequence().into_iter().map(|x| json::from_str(x).unwrap())?;
        let v = v.as_sequence().context("no results found").unwrap();
        let num_results = if let redis::Value::Int(i) = &v[0] {
            i
        } else {
            panic!("failed to parse search result");
        };

        if *num_results == 0 {
            panic!("no results");
        }

        let key = if let redis::Value::BulkString(i) = &v[1] {
            std::str::from_utf8(i).unwrap()
        } else {
            panic!("failed to parse search result");
        };

        let data = if let redis::Value::BulkString(i) = &v[2].as_sequence().unwrap()[1] {
            let s = std::str::from_utf8(&i).unwrap();
            json::from_str::<Professor>(s).unwrap()
        } else {
            panic!("failed to parse search result");
        };

        //let results = v.into_iter().map(|result| {}).collect;

        Ok(data)
    }
}

impl redis::FromRedisValue for Publication {
    fn from_redis_value(v: &redis::Value) -> redis::RedisResult<Self> {
        todo!()
    }
}
