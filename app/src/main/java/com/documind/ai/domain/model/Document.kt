package com.documind.ai.domain.model

/**
 * Domain model for business documents processed by DocuMind AI.
 */
data class Document(
    val id: String,
    val fileName: String,
    val documentType: String,
    val status: String,
    val dateAdded: String
)
