mod models;
mod config;
// use serde::{Serialize, Deserialize};
use std::error::Error;

async fn call_api(doc_type: &str) ->  Result<models::ApiResponse, Box<dyn Error>>{
    let full_url = format!("{}{}", config::BASE_URL, doc_type);
    let response = reqwest::get(&full_url).await?;
    let api_response: models::ApiResponse = response
        .json()
        .await?;
    Ok(api_response)
}
// fn clean_data(Vec<AD>) -> Result<Vec()>
// fn get_all_docs(String doc_type) -> Array<Struct>
#[tokio::main]
async fn main() -> Result<(), reqwest::Error> {
//    let client = reqwest::Client::new();
//    let ads: Vec<models::ApiResponse> = client
//        .get("https://drs.faa.gov/api/drs/data-pull/ADFRAWD")
//        .header("x-api-key", "3cc99314a05bcef0a82a3aeb7b95d031")
//        .send()
//        .await?
//        .json()
//        .await?;
    let doc_type: &str = "ADFRAWD";
    let ads = call_api(doc_type)
        .await;

    match result {
        Ok(ads) => println!("{:#?}", ads),
        Err(e) => eprintln!("Error: {:?}", e),
    }
}
