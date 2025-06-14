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
async function generateDiagram(isIteration = false) {
    const prompt = document.getElementById('diagramPrompt').value.trim();
    const diagramType = document.getElementById('diagramType').value;
    
    if (!prompt) {
        showError('Please enter a description for your diagram');
        return;
    }
    
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
                is_iteration: isIteration
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('syntaxEditor').value = data.syntax;
            updateDiagram();
            document.getElementById('diagramPrompt').value = ''; // Clear prompt after generation
            updateIterationUI();
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

// Generate iteration
async function generateIteration() {
    await generateDiagram(true);
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
        } catch (error) {
            console.error('Error clearing session:', error);
            showError('Failed to clear session');
        }
    }
}

// Update iteration UI based on session state
async function updateIterationUI() {
    try {
        const response = await fetch('/api/session-info');
        const data = await response.json();
        
        if (data.success) {
            const hasCurrentDiagram = data.has_current_diagram;
            const iterateBtn = document.getElementById('iterateBtn');
            const newDiagramBtn = document.getElementById('newDiagramBtn');
            
            if (iterateBtn) {
                iterateBtn.disabled = !hasCurrentDiagram;
                iterateBtn.title = hasCurrentDiagram ? 'Add to current diagram' : 'No current diagram to iterate on';
            }
            
            if (newDiagramBtn) {
                newDiagramBtn.disabled = !hasCurrentDiagram;
            }
        }
    } catch (error) {
        console.error('Error updating iteration UI:', error);
    }
}

// Update diagram from syntax
async function updateDiagram() {
    const syntax = document.getElementById('syntaxEditor').value.trim();
    const diagramContainer = document.getElementById('diagramContainer');
    
    if (!syntax) {
        diagramContainer.innerHTML = `
            <div class="text-center text-muted mt-5">
                <i class="fas fa-project-diagram fa-3x mb-3"></i>
                <p>Your diagram will appear here</p>
            </div>
        `;
        return;
    }
    
    try {
        // Clear previous content
        diagramContainer.innerHTML = '<div id="mermaidDiagram"></div>';
        
        // Render the diagram
        const { svg } = await mermaid.render('mermaidDiagram', syntax);
        diagramContainer.innerHTML = svg;
        
        hideError();
    } catch (error) {
        console.error('Mermaid error:', error);
        showError(`Syntax error: ${error.message}`);
    }
}

// Debounced update function for real-time editing
const updateDiagramDebounced = debounce(updateDiagram, 500);

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
        
        // Get SVG dimensions
        const svgWidth = svgClone.getAttribute('width') || svgClone.viewBox.baseVal.width || 800;
        const svgHeight = svgClone.getAttribute('height') || svgClone.viewBox.baseVal.height || 600;
        
        // Create canvas
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Set canvas dimensions with scale factor for better quality
        const scale = 2;
        canvas.width = parseInt(svgWidth) * scale;
        canvas.height = parseInt(svgHeight) * scale;
        
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
                ctx.fillRect(0, 0, parseInt(svgWidth), parseInt(svgHeight));
                
                // Draw the image
                ctx.drawImage(img, 0, 0, parseInt(svgWidth), parseInt(svgHeight));
                
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

// Initial load
document.addEventListener('DOMContentLoaded', function() {
    // Focus on the prompt input
    document.getElementById('diagramPrompt').focus();
    
    // Update iteration UI on load
    updateIterationUI();
});