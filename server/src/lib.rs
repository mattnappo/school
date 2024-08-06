use std::time;
use std::process;
use std::thread;

use anyhow::Result;
use redis;

struct Server {
    rdb: redis::Client,
    conn: redis::Connection,
}


impl Server {
    pub fn new() -> Result<Self> {
        let cmd = process::Command::new("redis-server").spawn()?;
        let client = redis::Client::open("redis://127.0.0.1/")?;
        let conn = client.get_connection()?;

        // Wait until redis is ready
        loop {
            let pong = process::Command::new("redis-server").arg("ping").output()?.stdout;
            let pong = String::from_utf8(pong)?;
            if pong == "PONG" {
                break;
            }
            println!("waiting for redis");
            thread::sleep(time::Duration::from_millis(200));
        }

        println!("made new server");

        Ok(Server {
            rdb: client,
            conn
        })
    }
}

impl Drop for Server {
    fn drop(&mut self) {
        redis::cmd("SHUTDOWN").arg("nosave").query::<()>(&mut self.conn).unwrap();
        //let x = process::Command::new("redis-cli").arg("shutdown").output().unwrap();
        //dbg!(x);
    }
}

#[cfg(test)]
pub mod tests {
    use super::*;

    #[test]
    fn test_start() -> Result<()> {
        let _server = Server::new()?;

        Ok(())
    }
}

