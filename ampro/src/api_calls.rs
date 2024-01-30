use crate::config;
use crate::models::{ApiDocuments, ApiResponse, ApiSummary}; //use reqwest::blocking::ClientBuilder;
use reqwest::header::{HeaderMap, HeaderValue};
use reqwest::Client;
use reqwest::ClientBuilder;
use reqwest::Url;
use std::env;
use std::error::Error;
use std::time::Duration;

pub async fn call_api(
    doc_type: &str,
    offset: Option<u32>,
    last_date_modified: Option<&str>,
) -> Result<ApiResponse, Box<dyn std::error::Error>> {
    let timeout = Duration::new(10, 0);
    let client = ClientBuilder::new()
        .timeout(timeout)
        .danger_accept_invalid_certs(true)
        .build()?;

    let url_w_query = create_url(doc_type, offset, last_date_modified)?; //    let url_w_query = format!("{}?offset=0", create_url(doc_type));
                                                                         //
    let mut headers = HeaderMap::new();
    let api_key = env::var("DRS_API_KEY").expect("DRS_API_KEY must be set");

    headers.insert("x-api-key", api_key.parse().unwrap());
    headers.insert(
        reqwest::header::USER_AGENT,
        HeaderValue::from_static("curl/7.68.0"),
    );

    log::debug!("Headers: {:?}", headers);

    log::debug!("Request URL: {}", url_w_query);

    let response = client.get(url_w_query).headers(headers).send().await?;

    let response_status = &response.status();

    if response_status.is_success() {
        println!("Request successful with status: {:?}", response_status);
    } else {
        println!("Request failed with status: {}", &response.status());
    }
    //let response = client.get(url_w_query).headers(headers).send().await?;
    log::info!("finished the api call with status: {}", response_status);

    let api_response = response.json::<ApiResponse>().await?;

    Ok(api_response)
}
fn create_client(timeout_duration: Option<Duration>) -> Result<Client, Box<dyn std::error::Error>> {
    log::info!("Creating a client to call API...");
    let api_key = env::var("DRS_API_KEY").expect("DRS_API_KEY must be set");

    let timeout = timeout_duration.unwrap_or(Duration::new(10, 0));

    let client = ClientBuilder::new()
        .timeout(timeout_duration.expect("Invalid timeout duration"))
        .build()?;

    let mut headers = HeaderMap::new();
    headers.insert(
        reqwest::header::USER_AGENT,
        HeaderValue::from_static("curl/7.68.0"),
    );
    headers.insert("x-api-key", api_key.parse().unwrap());

    log::debug!("Client: {:?}", client);
    log::debug!("Headers: {:?}", headers);

    Ok(client)
}

fn create_url(
    doc_type: &str,
    offset: Option<u32>,
    last_date_modified: Option<&str>,
) -> Result<Url, url::ParseError> {
    log::info!("Creating a url");

    let base_url = format!("{}{}", config::BASE_URL, doc_type);
    let mut url = Url::parse(&base_url)?;

    {
        let mut query_params = url.query_pairs_mut();

        let offset_val = offset.unwrap_or(0).min(config::MAX_OFFSET);
        query_params.append_pair("offset", &offset_val.to_string());

        if let Some(date) = last_date_modified {
            query_params.append_pair("dateLastModified", date);
        }
    }

    Ok(url)
}

fn get_summary(response: &ApiResponse) -> Result<&ApiSummary, url::ParseError> {
    let total_documents = &response.summary;

    Ok(total_documents)
}

fn get_documents(response: &ApiResponse) -> Result<(), Box<dyn std::error::Error>> {
    //Result<Vec<ApiDocuments>, Box<dyn Error>> {
    log::info!("Parsing documents from API response...");

    Ok(())
}

pub fn get_total_num_docs(api_summary: &ApiResponse) -> Result<u32, url::ParseError> {
    let total_documents = api_summary.summary.total_items;

    Ok(total_documents)
}
