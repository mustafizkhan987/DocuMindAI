package com.documind.ai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.documind.ai.core.navigation.AppNavigation
import com.documind.ai.ui.theme.DocuMindAITheme

/**
 * DocuMind AI — Main Activity
 *
 * Task 3: Android Application Foundation
 *
 * Entry point activity for DocuMind AI. Sets up edge-to-edge display
 * and launches AppNavigation (Home, Documents, Settings, Overview screens)
 * using Jetpack Compose and MVVM architecture.
 */
class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            DocuMindAITheme(darkTheme = true) {
                Surface(modifier = Modifier.fillMaxSize()) {
                    AppNavigation()
                }
            }
        }
    }
}