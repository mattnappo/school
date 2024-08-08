use anyhow::{bail, Result};
use redis::{RedisResult, Value};
use serde::{Deserialize, Serialize};

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

fn redis_to_int(v: &redis::Value) -> Result<i64> {
    match v {
        redis::Value::Int(i) => Ok(*i),
        _ => bail!("failed to parse int, but {v:?} supplied"),
    }
}

fn redis_to_string(v: &redis::Value) -> Result<String> {
    match v {
        redis::Value::BulkString(s) => Ok(std::str::from_utf8(s)?.to_string()),
        _ => bail!("failed to parse String, but {v:?} supplied"),
    }
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Publications(Vec<Publication>);

impl Publications {
    pub fn inner(self) -> Vec<Publication> {
        self.0
    }
}

macro_rules! redis_err {
    ($msg:literal) => {
        Err(redis::RedisError::from((
            redis::ErrorKind::ParseError,
            $msg,
        )))
    };
}

macro_rules! map_redis_err {
    ($e:expr, $msg:literal) => {
        $e.map_err(|_| {
            eprintln!("{}", $msg);
            redis::RedisError::from((redis::ErrorKind::ParseError, $msg))
        })
    };
}

impl redis::FromRedisValue for Publications {
    fn from_redis_value(v: &Value) -> RedisResult<Self> {
        match v {
            Value::Array(array) => {
                let len = map_redis_err!(redis_to_int(&array[0]), "failed to parse array length")?
                    as usize;
                if len == 0 {
                    return Ok(Publications(vec![]));
                }

                let pubs: RedisResult<Vec<Publication>> = array
                    .iter()
                    .skip(2)
                    .step_by(2)
                    .map(|res| {
                        // println!("{res:#?}");
                        if let Value::Array(inner_array) = &res {
                            if inner_array.len() != 2 {
                                return redis_err!("invalid inner array length (expected 2)");
                            }

                            if let Value::BulkString(json_bytes) = &inner_array[1] {
                                map_redis_err!(
                                    serde_json::from_slice::<Publication>(&json_bytes),
                                    "failed to parse json payload"
                                )
                            } else {
                                redis_err!("expected bulk-string for json data")
                            }
                        } else {
                            redis_err!("expected inner array")
                        }
                    })
                    .collect();

                Ok(Publications(pubs?))
            }
            _ => redis_err!("expected outer array"),
        }
    }
}
