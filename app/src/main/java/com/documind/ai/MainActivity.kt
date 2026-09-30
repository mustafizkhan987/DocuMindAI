package com.documind.ai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.documind.ai.ui.screens.FoundationScreen
import com.documind.ai.ui.theme.DocuMindAITheme

/**
 * DocuMind AI — Main Activity
 *
 * Task 1: Project Foundation
 *
 * Entry point activity for DocuMind AI. Sets up edge-to-edge display
 * and renders the FoundationScreen using Jetpack Compose.
 *
 * Task 1 shows: App identity + backend connectivity status + feature roadmap.
 * Task 4 will replace the simulated backend check with a real API call.
 */
class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            DocuMindAITheme(darkTheme = true) {
                Surface(modifier = Modifier.fillMaxSize()) {
                    FoundationScreen()
                }
            }
        }
    }
}