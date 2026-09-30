package com.documind.ai.ui.screens.home

import com.documind.ai.domain.model.Document

/**
 * UI State representation for the DocuMind AI Home Screen.
 */
data class HomeUiState(
    val backendConnected: Boolean = false,
    val backendStatusMessage: String = "Not Connected",
    val isLoading: Boolean = false,
    val recentDocuments: List<Document> = emptyList(),
    val error: String? = null
)
