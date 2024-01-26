mod models;
mod api_calls;
mod config;
// use serde::{Serialize, Deserialize};
// use std::error::Error;
//
//async fn call_api(doc_type: &str) ->  Result<models::ApiResponse, Box<dyn Error>>{
//    log::info!("Starting API call to DRS system.");
//    let full_url_test = api_calls::create_url(doc_type);
//    log::info!("full_url_test: {}", full_url_test);
//    let full_url = format!("{}{}", config::BASE_URL, doc_type);
//    log::info!("The full URL is: {}", &full_url);
//    let api_response = api_calls::call_api(doc_type);
////    let client = reqwest::Client::new();
////
////    let mut header = HeaderMap::new();
////    header.insert("x-api-key", "3cc99314a05bcef0a82a3aeb7b95d031".parse().unwrap());
////    log::info!("The header is: {:#?}", header);
////    let response = match client.get(&full_url)
////        .headers(header)
////        .send()
////        .await {
////            Ok(resp) => {
////                log::info!("Received response from {}", &full_url);
////                resp
////            },
////            Err(e) => {
////                log::info!("Error sending request to {}: {:?}", &full_url, e);
////                return Err(Box::new(e));
////            }
////        };
////    
////    log::info!("A response was received!");
//////    let response = reqwest::get(&full_url).await?;
////    let api_response: models::ApiResponse = response
// //       .json()
//  //      .await?;
//    log::info!("API call successfull. Returning value to main()");
//    Ok(api_response)
//}
// fn clean_data(Vec<AD>) -> Result<Vec()>
// fn get_all_docs(String doc_type) -> Array<Struct>

#[tokio::main]
async fn main() -> Result<(), reqwest::Error> {
    env_logger::init();
//    let client = reqwest::Client::new();
//    let ads: Vec<models::ApiResponse> = client
//        .get("https://drs.faa.gov/api/drs/data-pull/ADFRAWD")
//        .header("x-api-key", "3cc99314a05bcef0a82a3aeb7b95d031")
//        .send()
//        .await?
//        .json()
//        .await?;
    log::info!("Starting main()");
    let doc_type: &str = "ADFRAWD";
    log::info!("Using doc_type {}", &doc_type);
    let result = api_calls::call_api(doc_type)


    match  result{
        Ok(ads) => println!("{:#?}", ads),
        Err(e) => eprintln!("Error: {:?}", e),
    }
    Ok(())
}
