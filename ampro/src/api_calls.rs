use crate::models;
use crate::config;
use reqwest::Client;

pub fn call_api(doc_type: &str) -> Result<models::ApiResponse, Box<dyn std::error::Error>>{
    let http_client: Client = Client::new();
    let url_w_query = format!("{}?offset=0", create_url(doc_type));
    log::info!("URL with query: {}", url_w_query);
    let http_result = http_client
        .get(url_w_query)
        .header("x-api-key", "3cc99314a05bcef0a82a3aeb7b95d031")
//        .query(&[("offset", "0")])
        .send()
        .json::<models::ApiResponse>()
        //http_client.get(url: create_url)
    Ok(http_result)
}

pub fn create_url(doc_type: &str) -> String {
    log::info!("Creating URL...");
    let full_url: String = format!("{}{}", config::BASE_URL, doc_type);

//    log::info!("Full URl for reqwest: {}",full_url);
    full_url

}
