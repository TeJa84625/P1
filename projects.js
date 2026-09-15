// projects.js - 100% Static Frontend (No APIs)

const projectsGridElement = document.getElementById('projectsGrid');
const projectListSpinnerContainer = document.getElementById('projectListSpinnerContainer');
const projectSearchInput = document.getElementById('projectSearchInput');
const clearSearchButton = document.getElementById('clearSearchButton');
const technologyFilter = document.getElementById('technologyFilter');
const tagsFilter = document.getElementById('tagsFilter');
const statusFilter = document.getElementById('statusFilter');
const sortFilter = document.getElementById('sortFilter');
const clearFiltersButton = document.getElementById('clearFiltersButton');
const noProjectsMessage = document.getElementById('noProjectsMessage');
const loadingScreen = document.getElementById('loadingScreen');
const paginationContainer = document.getElementById('paginationContainer'); 

let allProjectsData = [];
let filteredAndSortedProjects = [];
let currentPage = 1;
const projectsPerPage = 9;

// --- Data Fetching (Direct JSON File Read) ---
async function fetchProjects() {
    try {
        if(projectListSpinnerContainer) projectListSpinnerContainer.style.display = 'flex';

        // Fetching the statically built projects.json file (cache-busting included)
        // Works on Vercel, Netlify, GitHub Pages, or any basic web server
        const response = await fetch('projects/projects.json?t=' + Date.now());
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const projects = await response.json();
        return projects;
    } catch (error) {
        console.error("Error fetching static projects.json: ", error);
        return [];
    } finally {
        if(projectListSpinnerContainer) projectListSpinnerContainer.style.display = 'none';
    }
}

// --- Filtering and Sorting ---
function populateFilters() {
    const uniqueTechnologies = new Set();
    const uniqueTags = new Set();

    allProjectsData.forEach(project => {
        (project.technologies || []).forEach(tech => uniqueTechnologies.add(tech.trim()));
        (project.tags || []).forEach(tag => uniqueTags.add(tag.trim()));
    });

    technologyFilter.innerHTML = '<option value="">All Technologies</option>';
    Array.from(uniqueTechnologies).sort().forEach(tech => {
        if (tech) {
            const option = document.createElement('option');
            option.value = tech;
            option.textContent = tech;
            technologyFilter.appendChild(option);
        }
    });

    tagsFilter.innerHTML = '<option value="">All Tags</option>';
    Array.from(uniqueTags).sort().forEach(tag => {
        if (tag) {
            const option = document.createElement('option');
            option.value = tag;
            option.textContent = tag;
            tagsFilter.appendChild(option);
        }
    });
}

function getProjectDate(project) {
    const dateString = project.upload_date || project.last_updated;
    return dateString ? new Date(dateString) : new Date(0);
}

function filterProjects() {
    const searchTerm = projectSearchInput.value.toLowerCase().trim();
    const selectedTechnology = technologyFilter.value.toLowerCase();
    const selectedTag = tagsFilter.value.toLowerCase();
    const selectedStatus = statusFilter.value.toLowerCase();
    const selectedSort = sortFilter.value;

    let tempFilteredProjects = allProjectsData.filter(project => {
        const name = (project.projectName || project.id || '').toLowerCase();
        const shortDesc = (project.short_description || '').toLowerCase();
        const longDesc = (project.long_description || '').toLowerCase();
        const technologies = (project.technologies || []).map(t => t.toLowerCase());
        const tags = (project.tags || []).map(t => t.toLowerCase());
        const status = (project.project_status || '').toLowerCase();

        const matchesSearch = !searchTerm || name.includes(searchTerm) || shortDesc.includes(searchTerm) || longDesc.includes(searchTerm);
        const matchesTechnology = !selectedTechnology || technologies.includes(selectedTechnology);
        const matchesTag = !selectedTag || tags.includes(selectedTag);
        const matchesStatus = !selectedStatus || status === selectedStatus;

        return matchesSearch && matchesTechnology && matchesTag && matchesStatus;
    });

    switch (selectedSort) {
        case 'name_asc':
            tempFilteredProjects.sort((a, b) => (a.projectName || a.id).localeCompare(b.projectName || b.id));
            break;
        case 'date_desc':
            tempFilteredProjects.sort((a, b) => getProjectDate(b) - getProjectDate(a));
            break;
        case 'date_asc':
            tempFilteredProjects.sort((a, b) => getProjectDate(a) - getProjectDate(b));
            break;
        case 'views_desc':
            tempFilteredProjects.sort((a, b) => (b.views || 0) - (a.views || 0));
            break;
        case 'views_asc':
            tempFilteredProjects.sort((a, b) => (a.views || 0) - (b.views || 0));
            break;
    }

    filteredAndSortedProjects = tempFilteredProjects;
    currentPage = 1; 

    renderPaginatedProjects();
    
    if (filteredAndSortedProjects.length === 0 && (searchTerm || selectedTechnology || selectedTag || selectedStatus)) {
        noProjectsMessage.classList.remove('hidden-message');
    } else {
        noProjectsMessage.classList.add('hidden-message');
    }
}

// --- Pagination and Rendering ---
function renderPaginatedProjects() {
    const startIndex = (currentPage - 1) * projectsPerPage;
    const endIndex = startIndex + projectsPerPage;
    const projectsToRender = filteredAndSortedProjects.slice(startIndex, endIndex);

    renderProjectCards(projectsToRender);
    renderPaginationControls(filteredAndSortedProjects.length);
}

function goToPage(pageNumber) {
    currentPage = pageNumber;
    renderPaginatedProjects();
    if (projectsGridElement) {
        projectsGridElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function renderPaginationControls(totalProjects) {
    const totalPages = Math.ceil(totalProjects / projectsPerPage);
    paginationContainer.innerHTML = ''; 

    if (totalPages <= 1) return;

    const prevButton = document.createElement('button');
    prevButton.textContent = 'Previous';
    prevButton.className = `px-4 py-2 mx-1 rounded-lg ${currentPage === 1 ? 'bg-gray-300 dark:bg-gray-700 text-gray-500 cursor-not-allowed' : 'bg-blue-600 text-white hover:bg-blue-700'}`;
    prevButton.disabled = currentPage === 1;
    prevButton.onclick = () => goToPage(currentPage - 1);
    paginationContainer.appendChild(prevButton);

    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, currentPage + 2);

    if (currentPage <= 3) { endPage = Math.min(totalPages, 5); } 
    else if (currentPage > totalPages - 3) { startPage = Math.max(1, totalPages - 4); }

    if (startPage > 1) {
        paginationContainer.appendChild(createPageButton(1, currentPage));
        if (startPage > 2) {
            const ellipsis = document.createElement('span');
            ellipsis.textContent = '...'; ellipsis.className = 'px-2 text-gray-500';
            paginationContainer.appendChild(ellipsis);
        }
    }

    for (let i = startPage; i <= endPage; i++) {
        paginationContainer.appendChild(createPageButton(i, currentPage));
    }

    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            const ellipsis = document.createElement('span');
            ellipsis.textContent = '...'; ellipsis.className = 'px-2 text-gray-500';
            paginationContainer.appendChild(ellipsis);
        }
        paginationContainer.appendChild(createPageButton(totalPages, currentPage));
    }

    const nextButton = document.createElement('button');
    nextButton.textContent = 'Next';
    nextButton.className = `px-4 py-2 mx-1 rounded-lg ${currentPage === totalPages ? 'bg-gray-300 dark:bg-gray-700 text-gray-500 cursor-not-allowed' : 'bg-blue-600 text-white hover:bg-blue-700'}`;
    nextButton.disabled = currentPage === totalPages;
    nextButton.onclick = () => goToPage(currentPage + 1);
    paginationContainer.appendChild(nextButton);
}

function createPageButton(page, activePage) {
    const button = document.createElement('button');
    button.textContent = page;
    button.onclick = () => goToPage(page);
    button.className = `px-4 py-2 mx-1 rounded-lg transition-colors duration-200 ${
        page === activePage 
        ? 'bg-blue-600 text-white font-bold shadow-md' 
        : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 border border-gray-300 dark:border-gray-600'
    }`;
    return button;
}

// --- Dynamic HTML Template Engine ---
function renderProjectCards(projects) {
    projectsGridElement.innerHTML = '';

    if (projects.length === 0) return;

    projects.forEach(project => {
        const title = project.projectName || project.id || 'Untitled Project';
        const desc = project.short_description || 'No description provided.';
        const img = (project.image_urls && project.image_urls.length > 0) ? project.image_urls[0] : `https://placehold.co/600x400?text=${encodeURIComponent(title)}`;
        const datePub = project.upload_date || '';
        
        const tags = project.tags || [];
        const tech = project.technologies || [];
        const keywords = [...tags, ...tech].join(', ');
        const urlSlug = project.url || encodeURIComponent(title.toLowerCase().replace(/\s+/g, '-')) + '.html';

        // --- Project Status & Color-Coding Logic ---
        const projectStatus = (project.project_status || 'unknown').trim().toLowerCase();
        let statusBadgeClass = 'bg-gray-400 text-gray-800';
        let statusText = project.project_status || 'N/A';
        
        if (projectStatus === 'ongoing') {
            statusBadgeClass = 'bg-yellow-500 text-yellow-900 font-bold';
            statusText = 'Ongoing';
        } else if (projectStatus === 'completed') {
            statusBadgeClass = 'bg-green-500 text-green-900 font-bold';
            statusText = 'Completed';
        } else if (projectStatus === 'onhold' || projectStatus === 'on hold') {
            statusBadgeClass = 'bg-red-500 text-red-900 font-bold';
            statusText = 'On Hold';
        }

        let techHtml = '';
        tech.slice(0, 4).forEach(t => {
            techHtml += `<span class="bg-blue-50 dark:bg-blue-900/40 text-blue-700 dark:text-blue-200 text-xs px-2.5 py-1 rounded-md font-semibold border border-blue-100 dark:border-blue-800" itemprop="applicationCategory">${t}</span>\n`;
        });

        const article = document.createElement('article');
        article.className = "project-card group bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-2xl transition-all duration-300 flex flex-col justify-between";
        article.setAttribute('itemscope', '');
        article.setAttribute('itemtype', 'https://schema.org/CreativeWork');
        article.setAttribute('role', 'listitem');

        article.innerHTML = `
            <header>
                <meta itemprop="datePublished" content="${datePub}">
                <meta itemprop="keywords" content="${keywords.replace(/"/g, '&quot;')}">
                
                <!-- Image Container with Absolute Status Badge -->
                <figure class="mb-5 overflow-hidden rounded-lg bg-gray-100 relative">
                    <div class="absolute top-2 right-2 px-3 py-1 text-xs rounded-full shadow-md ${statusBadgeClass} z-10">
                        ${statusText}
                    </div>
                    <img itemprop="image" src="${img}" alt="Preview screenshot of ${title}" class="w-full h-52 object-cover transform group-hover:scale-105 transition-transform duration-500 ease-out" loading="lazy" onerror="this.src='https://placehold.co/600x400?text=${encodeURIComponent(title)}'">
                </figure>

                <h3 itemprop="name" class="text-2xl font-bold mb-3 text-gray-900 dark:text-white leading-tight">
                    <a href="projects/${urlSlug}" itemprop="url" class="hover:text-blue-600 dark:hover:text-blue-400 focus:outline-none focus:underline transition-colors">
                        ${title}
                    </a>
                </h3>
            </header>

            <div class="flex-grow mb-5">
                <p itemprop="description" class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed line-clamp-3">
                    ${desc}
                </p>
            </div>

            <footer>
                <div class="mb-6" aria-label="Technologies used">
                    <h4 class="sr-only">Built with</h4>
                    <div class="flex flex-wrap gap-2">
                        ${techHtml}
                    </div>
                </div>
                <a itemprop="url" href="projects/${urlSlug}" class="inline-flex items-center justify-center w-full bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-bold py-3 px-5 rounded-lg transition-all focus:ring-4 focus:ring-blue-300 focus:outline-none" aria-label="View comprehensive details about ${title}">
                    View Project Details
                    <svg class="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path>
                    </svg>
                </a>
            </footer>
        `;

        projectsGridElement.appendChild(article);
    });
}

// --- Event Listeners ---
projectSearchInput.addEventListener('input', () => {
    filterProjects();
    clearSearchButton.style.display = projectSearchInput.value.trim() !== '' ? 'inline-block' : 'none';
});

clearSearchButton.addEventListener('click', () => {
    projectSearchInput.value = '';
    clearSearchButton.style.display = 'none';
    filterProjects();
});

technologyFilter.addEventListener('change', filterProjects);
tagsFilter.addEventListener('change', filterProjects);
statusFilter.addEventListener('change', filterProjects);
sortFilter.addEventListener('change', filterProjects);

clearFiltersButton.addEventListener('click', () => {
    technologyFilter.value = '';
    tagsFilter.value = '';
    statusFilter.value = '';
    sortFilter.value = '';
    filterProjects();
});

// Start Process
document.addEventListener('DOMContentLoaded', async () => {
    allProjectsData = await fetchProjects();
    populateFilters();
    filterProjects();
});