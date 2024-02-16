mod api_calls;
use dotenv::dotenv;
mod config;
mod models;

#[tokio::main]
async fn main() -> Result<(), reqwest::Error> {
    dotenv().ok();

    env_logger::init();
    log::info!("Starting main()");

    let doc_type: &str = "AD";
    let offset = Some(0); //Some(0u32);

    log::info!("Using doc_type {}", &doc_type);
    let api_response_future = api_calls::call_api(doc_type, offset, None);

    log::info!("Back in main.rs");

    //Get the total number of documents of the queried type so that we know how many api calls we
    match api_response_future.await {
        Ok(api_response_future) => {
            println!("Api response success: {:?}", api_response_future);
            let total_num_documents = api_response_future.summary.total_items;
            println!("Total Number of Documents: {}", total_num_documents);
        }
        Err(e) => {
            println!("Unable to complete request: {}", e);
        }
    }
    //need to do.
    Ok(())
}
