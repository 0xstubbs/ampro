use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct ApiResponse {
    pub summary: ApiSummary,
    pub documents: ApiDocuments,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ApiSummary {
    #[serde(rename = "doctypeName")]
    pub doc_type_name: String,
    #[serde(rename = "drsDoctypeName")]
    pub drs_doc_type_name: String,
    #[serde(rename = "count")]
    pub count: u32,
    #[serde(rename = "hasMoreItems")]
    pub has_more_items: bool,
    #[serde(rename = "totalItems")]
    pub total_items: u32,
    #[serde(rename = "offset")]
    pub offset: u32,
    #[serde(rename = "sortBy")]
    pub sort_by: String,
    #[serde(rename = "sortByOrder")]
    pub sort_by_order: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub enum ApiDocuments {
    ADs(ADStruct),
    ACs(ACStruct),
    // Add other variants for different document structures
}
#[derive(Serialize, Deserialize, Debug)]
pub struct ADStruct {
    #[serde(rename = "drs:documentNumber")]
    pub document_number: String,
    #[serde(rename = "drs:status")]
    pub status: String,
    #[serde(rename = "drs:adfrawdDocketNo")]
    pub docket_number: String,
    #[serde(rename = "drs:adfrawdAmendment")]
    pub amendment: String,
    #[serde(rename = "drs:adfrawdMake")]
    pub make: Vec<String>,
    #[serde(rename = "drs:adfrawdModel")]
    pub model: Vec<String>,
    #[serde(rename = "drs:adfrawdProductType")]
    pub product_type: Vec<String>,
    #[serde(rename = "drs:adfrawdProductSubType")]
    pub product_sub_type: Vec<String>,
    #[serde(rename = "drs:adfrawdSubject")]
    pub subject: String,
}
#[derive(Serialize, Deserialize, Debug)]
pub struct ACStruct {
    #[serde(rename = "drs:docu")]
    pub docu: String,
}
