package com.documind.ai.data.remote.dto

import com.google.gson.annotations.SerializedName

/**
 * Data Transfer Object for document upload API response.
 */
data class DocumentUploadResponseDto(
    @SerializedName("document_id") val documentId: String,
    @SerializedName("original_filename") val originalFilename: String,
    @SerializedName("stored_filename") val storedFilename: String,
    @SerializedName("content_type") val contentType: String,
    @SerializedName("size_bytes") val sizeBytes: Long,
    @SerializedName("upload_timestamp") val uploadTimestamp: String,
    @SerializedName("status") val status: String
)
