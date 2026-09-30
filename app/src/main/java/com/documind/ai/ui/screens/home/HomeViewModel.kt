package com.documind.ai.ui.screens.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.documind.ai.core.common.Result
import com.documind.ai.core.network.NetworkModule
import com.documind.ai.data.repository.DocumentRepositoryImpl
import com.documind.ai.domain.repository.DocumentRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

/**
 * ViewModel for the DocuMind AI Home Screen following MVVM architecture.
 */
class HomeViewModel(
    private val repository: DocumentRepository = DocumentRepositoryImpl(NetworkModule.provideDocuMindApi())
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        loadHomeData()
    }

    fun loadHomeData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            when (val healthResult = repository.getBackendHealth()) {
                is Result.Success -> {
                    _uiState.update {
                        it.copy(
                            backendConnected = healthResult.data.isConnected,
                            backendStatusMessage = healthResult.data.status,
                            isLoading = false
                        )
                    }
                }
                is Result.Error -> {
                    _uiState.update {
                        it.copy(
                            backendConnected = false,
                            backendStatusMessage = "Not Connected",
                            isLoading = false,
                            error = healthResult.message
                        )
                    }
                }
                is Result.Loading -> {
                    _uiState.update { it.copy(isLoading = true) }
                }
            }
        }
    }
}
