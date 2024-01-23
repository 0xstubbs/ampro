use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct ApiResponse {
    pub summary: Vec<String>,
    pub documents: Vec<Vec<String>>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ApiSummary {
    pub doc_type_name: String,
    pub drs_doc_type_name: String,
    pub count: u32,
    pub has_more_items: bool,
    pub total_items: u32,
    pub offset: u32,
    pub sort_by: String,
    pub sort_by_order: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ADFRAWD {
    #[serde(rename = "drs:documentNumber")]
    pub document_number: String,
    #[serde(rename = "drs:status")]
    pub status: String,
    #[serde(rename = "drs:adfrawdDocketNo")]
    pub docket_number: String,
    #[serde(rename="drs:adfrawdAmendment")]
    pub amendment: String,
    #[serde(rename = "drs:adfrawdMake")]
    pub make: Vec<String>,
}
// #[derive(Serialize, Deserialize, Debug)]
// pub struct ApiSummary {
// #}
