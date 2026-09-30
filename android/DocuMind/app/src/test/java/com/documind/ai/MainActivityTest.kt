package com.documind.ai

import org.junit.Test
import org.junit.Assert.*

/**
 * DocuMind AI — Unit Tests
 *
 * Task 1: Project Foundation
 *
 * Basic unit tests to verify the test framework is working.
 * More comprehensive tests will be added in later tasks.
 */
class MainActivityTest {

    @Test
    fun appVersion_isCorrect() {
        // Verify the expected version string
        val expectedVersion = "0.1.0"
        assertEquals("0.1.0", expectedVersion)
    }

    @Test
    fun packageName_isCorrect() {
        // Verify package naming convention
        val expectedPackage = "com.documind.ai"
        assertTrue(expectedPackage.startsWith("com.documind"))
    }
}
