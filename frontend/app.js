const API_BASE = "/events";

const eventsContainer = document.getElementById("events-container");
const loader = document.getElementById("loader");
const emptyState = document.getElementById("empty-state");
const filterBtns = document.querySelectorAll(".filter-btn");
const aiSearchInput = document.getElementById("ai-search-input");
const aiSearchBtn = document.getElementById("ai-search-btn");

let allEventsCache = [];

// Format Date Utility
function formatDate(dateString) {
    if (!dateString) return "TBA";
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Fetch events from API
async function fetchEvents() {
    showLoader();
    try {
        const response = await fetch(`${API_BASE}/?limit=500`);
        const data = await response.json();
        
        hideLoader();
        
        if (data.length === 0) {
            showEmptyState();
        } else {
            allEventsCache = data;
            // Initially render the default active filter (first button)
            const activeFilter = document.querySelector(".filter-btn.active").dataset.filter;
            renderEvents(activeFilter);
        }
    } catch (error) {
        console.error("Error fetching events:", error);
        hideLoader();
        showEmptyState();
        emptyState.innerHTML = `<h2>Error connecting to backend</h2><p>${error.message}. If deployed, check Vercel logs.</p>`;
    }
}

// Render groups
function renderEvents(filterType) {
    eventsContainer.innerHTML = "";
    eventsContainer.classList.remove("hidden");
    emptyState.classList.add("hidden");

    let eventsToShow = allEventsCache;
    if (filterType && filterType !== "all") {
        eventsToShow = allEventsCache.filter(e => (e.event_type || "").toLowerCase() === filterType);
    }

    if (eventsToShow.length === 0) {
        showEmptyState();
        return;
    }

    // Group events
    const grouped = {};
    eventsToShow.forEach(event => {
        const type = (event.event_type || "other").toLowerCase();
        if (!grouped[type]) grouped[type] = [];
        grouped[type].push(event);
    });

    const typeNames = {
        "competition": "Competitions",
        "hackathon": "Hackathons",
        "workshop": "Workshops",
        "quiz": "Quizzes",
        "conference": "Conferences",
        "cultural": "Cultural Events",
        "fest": "College Fests"
    };

    // Render each section
    for (const [type, events] of Object.entries(grouped)) {
        const section = document.createElement("section");
        section.className = "event-section";
        const title = document.createElement("h2");
        title.className = "section-title";
        title.textContent = typeNames[type] || (type.charAt(0).toUpperCase() + type.slice(1));
        
        const grid = document.createElement("div");
        grid.className = "events-grid";

        events.forEach(event => {
            const card = document.createElement("div");
            card.className = "event-card";
            
            let tagsHtml = (event.tags || []).map(tag => `<span class="tag">${tag}</span>`).join("");
            if (event.is_beginner_friendly) {
                tagsHtml = `<span class="tag beginner">🚀 Beginner Friendly</span>` + tagsHtml;
            }

            const priceClass = event.is_free ? "price free" : "price";
            const priceText = event.is_free ? "Free" : (event.prize || "Paid");
            
            let summaryHtml = "";
            if (event.summary) {
                const parts = event.summary.split(" | ");
                const keyPoints = parts.filter(p => p.includes("•") || ["Team of", "Solo", "Online", "Offline", "Prize:", "For Students"].some(k => p.includes(k)));
                const descParts = parts.filter(p => !keyPoints.includes(p));
                
                let keyPointsHtml = "";
                if (keyPoints.length > 0) {
                    const formattedPoints = keyPoints.map(p => {
                        const cleanP = p.replace(/[•|]/g, '').trim();
                        return cleanP ? `<span class="key-point">${cleanP}</span>` : '';
                    }).join('');
                    keyPointsHtml = `<div class="key-points">${formattedPoints}</div>`;
                }
                
                const descText = descParts.join(" ");
                summaryHtml = `<div class="ai-summary">✨ ${keyPointsHtml}${descText ? `<div class="desc-text">${descText}</div>` : ""}</div>`;
            }

            card.innerHTML = `
                <div class="card-header">
                    <span class="platform-badge">${event.platform}</span>
                    <span class="event-type">${event.event_type}</span>
                </div>
                <h2 class="event-title">${event.title}</h2>
                <div class="event-meta">
                    <div class="meta-item">📅 ${formatDate(event.event_date)} - ${formatDate(event.deadline)} (Deadline)</div>
                    <div class="meta-item">📍 ${event.location || "Online"}</div>
                </div>
                ${summaryHtml}
                <div class="tags-container">
                    ${tagsHtml}
                </div>
                <div class="card-footer">
                    <div class="${priceClass}">${priceText}</div>
                    <a href="${event.link}" target="_blank" class="view-btn">View Details</a>
                </div>
            `;
            grid.appendChild(card);
        });

        section.appendChild(title);
        section.appendChild(grid);
        eventsContainer.appendChild(section);
    }
}

function showLoader() {
    loader.classList.remove("hidden");
    eventsContainer.classList.add("hidden");
    emptyState.classList.add("hidden");
}

function hideLoader() {
    loader.classList.add("hidden");
}

function showEmptyState() {
    emptyState.classList.remove("hidden");
    eventsContainer.classList.add("hidden");
}

// Filter Logic
filterBtns.forEach(btn => {
    btn.addEventListener("click", (e) => {
        filterBtns.forEach(b => b.classList.remove("active"));
        e.target.classList.add("active");
        renderEvents(e.target.dataset.filter);
    });
});

// Initial Load
document.addEventListener("DOMContentLoaded", () => {
    fetchEvents();
});

// AI Search Logic
aiSearchBtn.addEventListener("click", () => {
    const query = aiSearchInput.value.trim();
    if (!query) return;
    fetchAISearch(query);
});

aiSearchInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        const query = aiSearchInput.value.trim();
        if (query) fetchAISearch(query);
    }
});

async function fetchAISearch(query) {
    showLoader();
    filterBtns.forEach(b => b.classList.remove("active"));
    
    try {
        const response = await fetch(`${API_BASE}/search`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: query })
        });
        const data = await response.json();
        
        hideLoader();
        
        if (!data.results || data.results.length === 0) {
            showEmptyState();
            emptyState.innerHTML = "<h2>No AI results found.</h2><p>Try rephrasing your search or ensure API keys are configured.</p>";
        } else {
            renderAIResults(data.query, data.results);
        }
    } catch (error) {
        console.error("Error fetching AI search:", error);
        hideLoader();
        showEmptyState();
        emptyState.innerHTML = `<h2>Error connecting to AI Search</h2><p>${error.message}. Ensure your API keys are set in Vercel env vars.</p>`;
    }
}

function renderAIResults(queryStr, results) {
    eventsContainer.innerHTML = "";
    eventsContainer.classList.remove("hidden");
    emptyState.classList.add("hidden");

    const section = document.createElement("section");
    section.className = "event-section";
    
    const title = document.createElement("h2");
    title.className = "section-title";
    title.innerHTML = `✨ AI Results for <span style="color:#4ECDC4;">"${queryStr}"</span>`;
    
    const grid = document.createElement("div");
    grid.className = "events-grid";

    results.forEach(event => {
        const card = document.createElement("div");
        card.className = "event-card";
        card.style.border = "1px solid rgba(78, 205, 196, 0.3)";
        
        card.innerHTML = `
            <div class="card-header">
                <span class="platform-badge" style="background: rgba(255,107,107,0.2); color:#FF6B6B;">${event.source}</span>
                <span class="event-type">AI Aggregated</span>
            </div>
            <h2 class="event-title">${event.title}</h2>
            <div class="event-meta">
                <div class="meta-item">📅 ${event.date || "TBA"}</div>
                <div class="meta-item">📍 ${event.location || "Unknown"}</div>
            </div>
            <div class="ai-summary">
                <div class="desc-text">${event.description}</div>
            </div>
            <div class="card-footer">
                <a href="${event.link}" target="_blank" class="view-btn" style="width: 100%;">View Details</a>
            </div>
        `;
        grid.appendChild(card);
    });

    section.appendChild(title);
    section.appendChild(grid);
    eventsContainer.appendChild(section);
}
