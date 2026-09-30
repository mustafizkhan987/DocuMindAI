package com.documind.ai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.documind.ai.ui.screens.FoundationScreen
import com.documind.ai.ui.theme.DocuMindTheme

/**
 * DocuMind AI — Main Activity
 *
 * Task 1: Project Foundation
 *
 * This is the single entry point activity for the DocuMind AI Android application.
 * It hosts the Compose UI and sets up edge-to-edge display.
 *
 * Task 1 scope:
 * - Launches FoundationScreen showing app identity and backend connectivity status
 *
 * Future tasks will:
 * - Add navigation graph (Task 3+)
 * - Add authentication flow (Task 3+)
 * - Add document upload flow (Task 5+)
 */
class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            DocuMindTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    FoundationScreen()
                }
            }
        }
    }
}
