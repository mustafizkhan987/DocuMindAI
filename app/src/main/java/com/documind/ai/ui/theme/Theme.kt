package com.documind.ai.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

private val LightColorScheme = lightColorScheme(
    primary = DocuMindPrimary,
    onPrimary = Color.White,
    primaryContainer = DocuMindPrimaryVariant,
    onPrimaryContainer = Color.White,
    secondary = DocuMindSecondary,
    onSecondary = Color.White,
    secondaryContainer = DocuMindSecondaryVariant,
    onSecondaryContainer = Color.White,
    tertiary = DocuMindAccent,
    background = LightBackground,
    onBackground = TextPrimary,
    surface = LightSurface,
    onSurface = TextPrimary,
    surfaceVariant = Color(0xFFF1F5F9),
    onSurfaceVariant = TextSecondary,
    outline = BorderLight,
    error = DocuMindError,
    onError = Color.White
)

@Composable
fun DocuMindAITheme(
    darkTheme: Boolean = false, // Force Light Mode as PRIMARY EXPERIENCE
    dynamicColor: Boolean = false, // Disable Material You to maintain brand consistency
    content: @Composable () -> Unit
) {
    val colorScheme = LightColorScheme

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.background.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = true
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}