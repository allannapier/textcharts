/**
 * Mermaid Diagram Builder JavaScript
 */

// Initialize Mermaid
mermaid.initialize({ 
    startOnLoad: false,
    theme: 'default',
    securityLevel: 'loose',
    fontFamily: 'Arial, sans-serif'
});

// Zoom and pan state
let currentZoom = 1.0;
let panX = 0;
let panY = 0;
const zoomStep = 0.2;
const minZoom = 0.1;
const maxZoom = 5.0;

// Pan state
let isPanning = false;
let startX = 0;
let startY = 0;
let startPanX = 0;
let startPanY = 0;

// Resizer state
let isResizing = false;
let startMouseX = 0;
let startLeftWidth = 0;

// Debounce function for real-time updates
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Generate diagram from prompt
async function generateDiagram(forceIteration = false) {
    const prompt = document.getElementById('diagramPrompt').value.trim();
    const diagramType = document.getElementById('diagramType').value;
    const currentSyntax = document.getElementById('syntaxEditor').value.trim();
    
    if (!prompt) {
        showError('Please enter a description for your diagram');
        return;
    }
    
    // Auto-detect if this should be an iteration:
    // - If forceIteration is explicitly false, never iterate (new diagram)
    // - If we have existing syntax and forceIteration is not false, iterate
    // - If syntax is empty, create new
    const shouldIterate = forceIteration !== false && currentSyntax.length > 0;
    
    console.log('Generate diagram:', {
        prompt: prompt.substring(0, 50) + '...',
        currentSyntax: currentSyntax.substring(0, 50) + '...',
        forceIteration,
        shouldIterate,
        syntaxLength: currentSyntax.length
    });
    
    showLoading(true);
    hideError();
    
    try {
        const response = await fetch('/api/generate-diagram', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt: prompt,
                diagram_type: diagramType,
                is_iteration: shouldIterate
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('syntaxEditor').value = data.syntax;
            updateDiagram();
            document.getElementById('diagramPrompt').value = ''; // Clear prompt after generation
            updateIterationUI();
            saveDiagramToLocalStorage();
        } else {
            showError(data.error || 'Failed to generate diagram');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('An error occurred while generating the diagram');
    } finally {
        showLoading(false);
    }
}

// Force new diagram (ignore existing syntax)
async function generateNewDiagram() {
    await generateDiagram(false);
}

// Clear session and start fresh
async function clearSession() {
    if (confirm('Are you sure you want to start a new diagram? This will clear your current work.')) {
        try {
            await fetch('/api/clear-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            document.getElementById('syntaxEditor').value = '';
            document.getElementById('diagramPrompt').value = '';
            updateDiagram();
            updateIterationUI();
            hideError();
            saveDiagramToLocalStorage();
        } catch (error) {
            console.error('Error clearing session:', error);
            showError('Failed to clear session');
        }
    }
}

// Save diagram to localStorage
function saveDiagramToLocalStorage() {
    try {
        const syntaxEditor = document.getElementById('syntaxEditor');
        const diagramType = document.getElementById('diagramType');
        
        const diagramData = {
            syntax: syntaxEditor.value,
            diagramType: diagramType.value,
            timestamp: new Date().toISOString()
        };
        
        localStorage.setItem('texaigram_current_diagram', JSON.stringify(diagramData));
    } catch (error) {
        console.log('Failed to save diagram to localStorage:', error);
        // Fail silently - localStorage might be disabled
    }
}

// Load diagram from localStorage
function loadDiagramFromLocalStorage() {
    try {
        const saved = localStorage.getItem('texaigram_current_diagram');
        if (saved) {
            const diagramData = JSON.parse(saved);
            
            // Only restore if we have syntax
            if (diagramData.syntax && diagramData.syntax.trim()) {
                document.getElementById('syntaxEditor').value = diagramData.syntax;
                document.getElementById('diagramType').value = diagramData.diagramType || 'flowchart';
                updateDiagram();
                return true;
            }
        }
    } catch (error) {
        console.log('Failed to load diagram from localStorage:', error);
        // Fail silently and continue
    }
    return false;
}

// Clear saved diagram from localStorage
function clearDiagramFromLocalStorage() {
    try {
        localStorage.removeItem('texaigram_current_diagram');
    } catch (error) {
        console.log('Failed to clear diagram from localStorage:', error);
    }
}

// Update UI based on current state
async function updateIterationUI() {
    try {
        const currentSyntax = document.getElementById('syntaxEditor').value.trim();
        const hasCurrentDiagram = currentSyntax.length > 0;
        
        const newDiagramBtn = document.getElementById('newDiagramBtn');
        const clearBtn = document.getElementById('clearBtn');
        const generateBtn = document.getElementById('generateBtn');
        
        // Enable "New Diagram" and "Clear All" only when there's existing content
        if (newDiagramBtn) {
            newDiagramBtn.disabled = !hasCurrentDiagram;
            newDiagramBtn.title = hasCurrentDiagram ? 'Create new diagram (ignore current)' : 'No current diagram';
        }
        
        if (clearBtn) {
            clearBtn.disabled = !hasCurrentDiagram;
            clearBtn.title = hasCurrentDiagram ? 'Clear everything and start fresh' : 'Nothing to clear';
        }
        
        // Update generate button text based on state
        if (generateBtn) {
            if (hasCurrentDiagram) {
                generateBtn.innerHTML = '<i class="fas fa-plus"></i> Add to Diagram';
                generateBtn.title = 'Add to existing diagram';
            } else {
                generateBtn.innerHTML = '<i class="fas fa-magic"></i> Generate';
                generateBtn.title = 'Create new diagram';
            }
        }
    } catch (error) {
        console.error('Error updating UI:', error);
    }
}

// Update diagram from syntax
async function updateDiagram() {
    const syntax = document.getElementById('syntaxEditor').value.trim();
    const diagramWrapper = document.getElementById('diagramWrapper');
    
    if (!syntax) {
        diagramWrapper.innerHTML = `
            <div class="text-center text-muted mt-5">
                <i class="fas fa-project-diagram fa-3x mb-3"></i>
                <p>Your diagram will appear here</p>
            </div>
        `;
        return;
    }
    
    try {
        // Clear previous content
        diagramWrapper.innerHTML = '<div id="mermaidDiagram"></div>';
        
        // Render the diagram
        const { svg } = await mermaid.render('mermaidDiagram', syntax);
        diagramWrapper.innerHTML = svg;
        
        // Reset zoom when new diagram is loaded
        resetZoom();
        
        hideError();
        updateIterationUI(); // Update UI when diagram changes
    } catch (error) {
        console.error('Mermaid error:', error);
        showError(`Syntax error: ${error.message}`);
    }
}

// Debounced update function for real-time editing
const updateDiagramDebounced = debounce(updateDiagram, 500);

// Apply zoom and pan transformations
function applyTransform() {
    const diagramWrapper = document.getElementById('diagramWrapper');
    const zoomIndicator = document.getElementById('zoomIndicator');
    
    if (diagramWrapper) {
        diagramWrapper.style.transform = `translate(${panX}px, ${panY}px) scale(${currentZoom})`;
        
        // Update zoom indicator
        const percentage = Math.round(currentZoom * 100);
        zoomIndicator.textContent = `${percentage}%`;
        
        // Show zoom indicator temporarily
        zoomIndicator.classList.add('show');
        setTimeout(() => {
            zoomIndicator.classList.remove('show');
        }, 1500);
    }
}

function zoomIn() {
    if (currentZoom < maxZoom) {
        currentZoom = Math.min(maxZoom, currentZoom + zoomStep);
        applyTransform();
    }
}

function zoomOut() {
    if (currentZoom > minZoom) {
        currentZoom = Math.max(minZoom, currentZoom - zoomStep);
        applyTransform();
    }
}

function resetZoom() {
    currentZoom = 1.0;
    panX = 0;
    panY = 0;
    applyTransform();
}

function fitToScreen() {
    const diagramContainer = document.getElementById('diagramContainer');
    const diagramWrapper = document.getElementById('diagramWrapper');
    const svg = diagramWrapper.querySelector('svg');
    
    if (!svg) return;
    
    // Get container and SVG dimensions
    const containerRect = diagramContainer.getBoundingClientRect();
    const svgRect = svg.getBoundingClientRect();
    
    // Calculate available space (accounting for padding)
    const availableWidth = containerRect.width - 40; // 20px padding on each side
    const availableHeight = containerRect.height - 40;
    
    // Calculate scale factors
    const scaleX = availableWidth / (svgRect.width / currentZoom);
    const scaleY = availableHeight / (svgRect.height / currentZoom);
    
    // Use the smaller scale to ensure the entire diagram fits
    const newZoom = Math.min(scaleX, scaleY, maxZoom);
    
    if (newZoom > minZoom) {
        currentZoom = newZoom;
        panX = 0;
        panY = 0;
        applyTransform();
    }
}

// Copy syntax to clipboard
async function copySyntax() {
    const syntax = document.getElementById('syntaxEditor').value;
    
    if (!syntax) {
        showError('No syntax to copy');
        return;
    }
    
    try {
        await navigator.clipboard.writeText(syntax);
        
        // Show temporary success message
        const btn = event.target.closest('button');
        const originalHtml = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i>';
        btn.classList.add('btn-success');
        btn.classList.remove('btn-outline-secondary');
        
        setTimeout(() => {
            btn.innerHTML = originalHtml;
            btn.classList.remove('btn-success');
            btn.classList.add('btn-outline-secondary');
        }, 2000);
    } catch (error) {
        console.error('Failed to copy:', error);
        showError('Failed to copy syntax');
    }
}

// Clear syntax
function clearSyntax() {
    if (confirm('Are you sure you want to clear the syntax?')) {
        document.getElementById('syntaxEditor').value = '';
        updateDiagram();
        hideError();
        saveDiagramToLocalStorage();
    }
}

// Export diagram as PNG
async function exportDiagram() {
    const syntax = document.getElementById('syntaxEditor').value.trim();
    
    if (!syntax) {
        showError('No diagram to export');
        return;
    }
    
    showLoading(true);
    
    try {
        // Create a temporary container for rendering
        const tempContainer = document.createElement('div');
        tempContainer.style.position = 'absolute';
        tempContainer.style.left = '-9999px';
        document.body.appendChild(tempContainer);
        
        // Render the diagram
        const { svg } = await mermaid.render('exportDiagram', syntax);
        tempContainer.innerHTML = svg;
        
        // Get the SVG element
        const svgElement = tempContainer.querySelector('svg');
        
        // Clean SVG to remove external references that cause CORS issues
        const svgClone = svgElement.cloneNode(true);
        
        // Remove any external image references
        const images = svgClone.querySelectorAll('image');
        images.forEach(img => img.remove());
        
        // Inline any styles to avoid CORS issues
        const styleSheets = Array.from(document.styleSheets);
        let inlineStyles = '';
        
        try {
            styleSheets.forEach(sheet => {
                if (sheet.href && sheet.href.includes('mermaid')) {
                    // Skip external mermaid stylesheets that might cause CORS
                    return;
                }
                try {
                    const rules = sheet.cssRules || sheet.rules;
                    if (rules) {
                        Array.from(rules).forEach(rule => {
                            inlineStyles += rule.cssText + '\n';
                        });
                    }
                } catch (e) {
                    // Skip inaccessible stylesheets
                }
            });
        } catch (e) {
            // Continue without inline styles if there are issues
        }
        
        // Add inline styles to SVG
        if (inlineStyles) {
            const styleElement = document.createElement('style');
            styleElement.textContent = inlineStyles;
            svgClone.insertBefore(styleElement, svgClone.firstChild);
        }
        
        // Get SVG dimensions - try multiple methods to get accurate dimensions
        let svgWidth, svgHeight;
        
        // Method 1: Try explicit width/height attributes
        const widthAttr = svgClone.getAttribute('width');
        const heightAttr = svgClone.getAttribute('height');
        
        if (widthAttr && heightAttr) {
            svgWidth = parseFloat(widthAttr.replace('px', ''));
            svgHeight = parseFloat(heightAttr.replace('px', ''));
        } else if (svgClone.viewBox && svgClone.viewBox.baseVal) {
            // Method 2: Use viewBox
            svgWidth = svgClone.viewBox.baseVal.width;
            svgHeight = svgClone.viewBox.baseVal.height;
        } else {
            // Method 3: Try to get computed dimensions from the displayed SVG
            const displayedSvg = document.querySelector('#diagramContainer svg');
            if (displayedSvg) {
                const rect = displayedSvg.getBoundingClientRect();
                svgWidth = rect.width;
                svgHeight = rect.height;
            } else {
                // Fallback dimensions
                svgWidth = 800;
                svgHeight = 600;
            }
        }
        
        // Ensure we have reasonable dimensions
        if (svgWidth < 100) svgWidth = 800;
        if (svgHeight < 100) svgHeight = 600;
        
        // Set explicit dimensions on the SVG to ensure proper scaling
        svgClone.setAttribute('width', svgWidth);
        svgClone.setAttribute('height', svgHeight);
        svgClone.setAttribute('viewBox', `0 0 ${svgWidth} ${svgHeight}`);
        
        // Create canvas
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Set canvas dimensions (2x for better quality)
        const scale = 2;
        canvas.width = svgWidth * scale;
        canvas.height = svgHeight * scale;
        
        // Scale context for high DPI
        ctx.scale(scale, scale);
        
        // Create data URL from cleaned SVG
        const svgData = new XMLSerializer().serializeToString(svgClone);
        const svgDataUrl = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
        
        const img = new Image();
        img.crossOrigin = 'anonymous'; // Handle CORS
        
        img.onload = function() {
            try {
                // Draw white background
                ctx.fillStyle = 'white';
                ctx.fillRect(0, 0, svgWidth, svgHeight);
                
                // Draw the image at correct dimensions
                ctx.drawImage(img, 0, 0, svgWidth, svgHeight);
                
                // Convert to PNG and download
                canvas.toBlob(function(blob) {
                    if (blob) {
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `texaigram_${new Date().getTime()}.png`;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);
                    } else {
                        showError('Failed to create image blob');
                    }
                }, 'image/png');
            } catch (canvasError) {
                console.error('Canvas error:', canvasError);
                showError('Failed to render diagram to canvas');
            }
            
            // Cleanup
            document.body.removeChild(tempContainer);
        };
        
        img.onerror = function() {
            showError('Failed to load diagram for export');
            document.body.removeChild(tempContainer);
        };
        
        img.src = svgDataUrl;
        
    } catch (error) {
        console.error('Export error:', error);
        showError('Failed to export diagram: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Show/hide loading overlay
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (show) {
        overlay.classList.remove('d-none');
    } else {
        overlay.classList.add('d-none');
    }
}

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('syntaxError');
    errorDiv.textContent = message;
    errorDiv.classList.remove('d-none');
}

// Hide error message
function hideError() {
    const errorDiv = document.getElementById('syntaxError');
    errorDiv.classList.add('d-none');
}

// Handle Enter key in prompt input
document.getElementById('diagramPrompt').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        generateDiagram();
    }
});

// Handle diagram type change
document.getElementById('diagramType').addEventListener('change', function() {
    // If there's already syntax, update the diagram
    const syntax = document.getElementById('syntaxEditor').value.trim();
    if (syntax) {
        updateDiagram();
    }
});

// Add mouse wheel zoom support
document.getElementById('diagramContainer').addEventListener('wheel', function(event) {
    // Only zoom if Ctrl key is pressed (common convention)
    if (event.ctrlKey || event.metaKey) {
        event.preventDefault();
        
        const delta = event.deltaY > 0 ? -1 : 1;
        const zoomAmount = delta * 0.1;
        
        const newZoom = Math.min(maxZoom, Math.max(minZoom, currentZoom + zoomAmount));
        if (newZoom !== currentZoom) {
            currentZoom = newZoom;
            applyTransform();
        }
    }
});

// Add pan functionality
function setupPanControls() {
    const diagramWrapper = document.getElementById('diagramWrapper');
    
    if (!diagramWrapper) return;
    
    // Mouse events for panning
    diagramWrapper.addEventListener('mousedown', function(event) {
        // Only pan if there's a diagram and we're not clicking on a diagram element
        const svg = diagramWrapper.querySelector('svg');
        if (!svg) return;
        
        // Prevent text selection and other default behaviors
        event.preventDefault();
        
        isPanning = true;
        startX = event.clientX;
        startY = event.clientY;
        startPanX = panX;
        startPanY = panY;
        
        diagramWrapper.classList.add('panning');
    });
    
    document.addEventListener('mousemove', function(event) {
        if (!isPanning) return;
        
        event.preventDefault();
        
        const deltaX = event.clientX - startX;
        const deltaY = event.clientY - startY;
        
        panX = startPanX + deltaX;
        panY = startPanY + deltaY;
        
        applyTransform();
    });
    
    document.addEventListener('mouseup', function() {
        if (isPanning) {
            isPanning = false;
            const diagramWrapper = document.getElementById('diagramWrapper');
            if (diagramWrapper) {
                diagramWrapper.classList.remove('panning');
            }
        }
    });
    
    // Touch events for mobile panning
    diagramWrapper.addEventListener('touchstart', function(event) {
        const svg = diagramWrapper.querySelector('svg');
        if (!svg || event.touches.length !== 1) return;
        
        event.preventDefault();
        
        isPanning = true;
        const touch = event.touches[0];
        startX = touch.clientX;
        startY = touch.clientY;
        startPanX = panX;
        startPanY = panY;
        
        diagramWrapper.classList.add('panning');
    });
    
    document.addEventListener('touchmove', function(event) {
        if (!isPanning || event.touches.length !== 1) return;
        
        event.preventDefault();
        
        const touch = event.touches[0];
        const deltaX = touch.clientX - startX;
        const deltaY = touch.clientY - startY;
        
        panX = startPanX + deltaX;
        panY = startPanY + deltaY;
        
        applyTransform();
    });
    
    document.addEventListener('touchend', function() {
        if (isPanning) {
            isPanning = false;
            const diagramWrapper = document.getElementById('diagramWrapper');
            if (diagramWrapper) {
                diagramWrapper.classList.remove('panning');
            }
        }
    });
}

// Setup resizer functionality
function setupResizer() {
    const resizer = document.getElementById('resizer');
    const leftPanel = document.getElementById('leftPanel');
    const rightPanel = document.getElementById('rightPanel');
    const container = leftPanel.parentElement;
    
    if (!resizer || !leftPanel || !rightPanel) return;
    
    resizer.addEventListener('mousedown', function(event) {
        isResizing = true;
        startMouseX = event.clientX;
        startLeftWidth = leftPanel.offsetWidth;
        
        // Prevent text selection during resize
        document.body.style.userSelect = 'none';
        document.body.style.cursor = 'col-resize';
        
        event.preventDefault();
    });
    
    document.addEventListener('mousemove', function(event) {
        if (!isResizing) return;
        
        event.preventDefault();
        
        const deltaX = event.clientX - startMouseX;
        const containerWidth = container.offsetWidth;
        const resizerWidth = resizer.offsetWidth;
        
        let newLeftWidth = startLeftWidth + deltaX;
        
        // Apply constraints
        const minLeftWidth = 300; // Minimum 300px for syntax panel
        const maxLeftWidth = containerWidth - resizerWidth - (containerWidth * 0.2); // Leave at least 20% for diagram
        
        newLeftWidth = Math.max(minLeftWidth, Math.min(maxLeftWidth, newLeftWidth));
        
        const leftPercentage = (newLeftWidth / containerWidth) * 100;
        const rightPercentage = ((containerWidth - newLeftWidth - resizerWidth) / containerWidth) * 100;
        
        // Update panel widths
        leftPanel.style.flex = `0 0 ${leftPercentage}%`;
        rightPanel.style.flex = `0 0 ${rightPercentage}%`;
        
        // Save the layout preference
        localStorage.setItem('texaigram_layout', JSON.stringify({
            leftPercentage,
            rightPercentage
        }));
    });
    
    document.addEventListener('mouseup', function() {
        if (isResizing) {
            isResizing = false;
            document.body.style.userSelect = '';
            document.body.style.cursor = '';
        }
    });
    
    // Prevent text selection when dragging over panels
    document.addEventListener('selectstart', function(event) {
        if (isResizing) {
            event.preventDefault();
        }
    });
}

// Load saved layout
function loadSavedLayout() {
    try {
        const saved = localStorage.getItem('texaigram_layout');
        if (saved) {
            const layout = JSON.parse(saved);
            const leftPanel = document.getElementById('leftPanel');
            const rightPanel = document.getElementById('rightPanel');
            
            if (leftPanel && rightPanel && layout.leftPercentage && layout.rightPercentage) {
                leftPanel.style.flex = `0 0 ${layout.leftPercentage}%`;
                rightPanel.style.flex = `0 0 ${layout.rightPercentage}%`;
            }
        }
    } catch (error) {
        console.log('Failed to load saved layout:', error);
    }
}

// Initial load
document.addEventListener('DOMContentLoaded', function() {
    // Try to load saved diagram first
    const loaded = loadDiagramFromLocalStorage();
    
    // Focus on the prompt input
    document.getElementById('diagramPrompt').focus();
    
    // Update iteration UI on load
    updateIterationUI();
    
    // Setup pan controls
    setupPanControls();
    
    // Setup resizer
    setupResizer();
    
    // Load saved layout
    loadSavedLayout();
    
    // If we loaded a diagram, show a subtle notification
    if (loaded) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-info alert-dismissible fade show position-fixed';
        alertDiv.style.top = '20px';
        alertDiv.style.right = '20px';
        alertDiv.style.zIndex = '9999';
        alertDiv.style.maxWidth = '300px';
        alertDiv.innerHTML = `
            <small><i class="fas fa-info-circle"></i> Restored your previous diagram</small>
            <button type="button" class="btn-close btn-close-sm" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alertDiv);
        
        // Auto-dismiss after 3 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 3000);
    }
});