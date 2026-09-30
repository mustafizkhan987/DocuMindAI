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

// DocuMind AI Brand Colors
// Primary: Deep professional navy/blue
val DocuMindPrimary = Color(0xFF0F2046)          
val DocuMindPrimaryVariant = Color(0xFF0A1530)   
val DocuMindSecondary = Color(0xFF2C7A7B)        // Muted teal
val DocuMindSecondaryVariant = Color(0xFF235F5F) 
val DocuMindAccent = Color(0xFF319795)           

// Semantic Colors
val DocuMindSuccess = Color(0xFF2F855A)          // Professional green
val DocuMindWarning = Color(0xFFC05621)          // Amber/orange
val DocuMindError = Color(0xFFC53030)            // Muted red

// Backgrounds and Surfaces
val LightBackground = Color(0xFFF7FAFC)
val LightSurface = Color(0xFFFFFFFF)
val DarkBackground = Color(0xFF1A202C)
val DarkSurface = Color(0xFF2D3748)
val DarkSurfaceVariant = Color(0xFF4A5568)

private val DarkColorScheme = darkColorScheme(
    primary = DocuMindPrimary,
    onPrimary = Color.White,
    primaryContainer = DocuMindPrimaryVariant,
    onPrimaryContainer = Color.White,
    secondary = DocuMindSecondary,
    onSecondary = Color.White,
    secondaryContainer = DocuMindSecondaryVariant,
    onSecondaryContainer = Color.White,
    tertiary = DocuMindAccent,
    background = DarkBackground,
    onBackground = Color(0xFFE2E8F0),
    surface = DarkSurface,
    onSurface = Color(0xFFE2E8F0),
    surfaceVariant = DarkSurfaceVariant,
    onSurfaceVariant = Color(0xFFCBD5E0),
    error = DocuMindError,
    onError = Color.White,
)

private val LightColorScheme = lightColorScheme(
    primary = DocuMindPrimary,
    onPrimary = Color.White,
    primaryContainer = Color(0xFFE2E8F0),
    onPrimaryContainer = DocuMindPrimary,
    secondary = DocuMindSecondary,
    onSecondary = Color.White,
    secondaryContainer = Color(0xFFE6FFFA),
    onSecondaryContainer = DocuMindSecondaryVariant,
    tertiary = DocuMindAccent,
    background = LightBackground,
    onBackground = Color(0xFF1A202C),
    surface = LightSurface,
    onSurface = Color(0xFF1A202C),
    surfaceVariant = Color(0xFFEDF2F7),
    onSurfaceVariant = Color(0xFF4A5568),
    error = DocuMindError,
    onError = Color.White,
)

/**
 * DocuMind AI Material3 Theme
 *
 * Uses dynamic color on Android 12+ for a modern adaptive experience.
 * Falls back to our brand color scheme on older Android versions.
 */
@Composable
fun DocuMindTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.primary.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = !darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
