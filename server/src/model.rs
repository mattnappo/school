use anyhow::{Context, Result};
use serde_json as json;

/*
macro_rules! field {
   ($item:expr, $field:expr) => {
       let $field = $item.get(stringify!($field)).context(concat!("missing field ", stringify!($field)))?.to_string();
   };
}
*/

#[derive(Debug)]
pub struct Professor {
    first: String,
    last: String,
    middle: Option<String>,
    website: String,
    pubs: Vec<Publication>,
}

#[derive(Debug)]
pub struct Publication {
    author: String,
    title: String,
    abstract_: String,
    url: String,
    pub_year: Option<u64>,
}

impl Professor {
    pub fn new(item: &json::Value) -> Result<Self> {
        let first = &item["first"];
        let last = &item["last"];
        let middle = if &item["middle"] == "" {
            None
        } else {
            Some(&item["middle"])
        };
        let website = &item["website"];

        let pubs = item["pubs"]
            .as_array()
            .unwrap_or(&vec![])
            .into_iter()
            .map(|p| Publication::new(&p).unwrap())
            .collect::<Vec<Publication>>();

        Ok(Professor {
            first: first.to_string(),
            last: last.to_string(),
            middle: middle.map(|n| n.to_string()),
            website: website.to_string(),
            pubs,
        })
    }
}

impl Publication {
    pub fn new(item: &json::Value) -> Result<Self> {
        let author = &item["author"];
        let title = &item["title"];
        let abstract_ = &item["abstract"];
        let url = &item["url"];
        let pub_year = {
            let y = item["pub_year"].as_u64().unwrap_or_default();
            if y == 0 {
                None
            } else {
                Some(y)
            }
        };

        Ok(Publication {
            author: author.to_string(),
            title: title.to_string(),
            abstract_: abstract_.to_string(),
            url: url.to_string(),
            pub_year,
        })
    }
}
