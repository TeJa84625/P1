import os
import json
import re
import html
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# --- Configuration & Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_DIR = os.path.join(BASE_DIR, 'projects')
PROJECTS_JSON = os.path.join(PROJECTS_DIR, 'projects.json')
PROJECT_HTML = os.path.join(BASE_DIR, 'projects.html')
SITEMAP_XML = os.path.join(BASE_DIR, 'sitemap.xml')
ROBOTS_TXT = os.path.join(BASE_DIR, 'robots.txt')

WEBSITE_URL = "https://tejagavara.vercel.app"

# --- 1. Initialization System ---
def check_and_create_structure():
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    if not os.path.exists(PROJECTS_JSON):
        with open(PROJECTS_JSON, 'w') as f: json.dump([], f)
    if not os.path.exists(PROJECT_HTML):
        with open(PROJECT_HTML, 'w') as f:
            f.write('<!DOCTYPE html>\n<html>\n<head>\n'
                    '    <title>Projects Portfolio</title>\n'
                    '    <script src="https://cdn.tailwindcss.com"></script>\n'
                    '</head>\n<body class="bg-gray-100 dark:bg-gray-900">\n'
                    '<!---------- JSON-LD Structured Data Start -->\n'
                    '<!---------- JSON-LD Structured Data End -->\n'
                    '<!---------- Projects Grid Start -->\n'
                    '<!---------- Projects Grid End -->\n'
                    '</body>\n</html>')

def load_projects():
    with open(PROJECTS_JSON, 'r') as f: return json.load(f)

def save_projects(projects):
    with open(PROJECTS_JSON, 'w') as f: json.dump(projects, f, indent=4)

def generate_slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

def get_youtube_id(url):
    if not url: return None
    match = re.search(r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})', url)
    return match.group(1) if match else None

# --- 2. HTML & SEO Generators ---
def build_json_ld_schema(projects):
    """Dynamically generates comprehensive SEO Schema.org JSON-LD structured data for projects.html using projects.json."""
    schema_items = []
    for p in projects:
        name = p.get('projectName', p.get('id', 'Untitled Project'))
        desc = p.get('short_description', 'Engineering project by Teja Gavara.')
        url = p.get('button_url', f"{WEBSITE_URL}/projects/{p.get('url', '')}")
        image = p.get('image_urls', [f"https://placehold.co/600x400?text={name.replace(' ', '+')}"])[0] if p.get('image_urls') else ""
        date_pub = p.get('upload_date', '2025-01-01')
        
        item = {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": name,
            "url": url,
            "applicationCategory": "DeveloperApplication",
            "operatingSystem": "Web, Android",
            "datePublished": date_pub,
            "description": desc,
            "image": image,
            "author": {
                "@type": "Person",
                "name": "Teja Gavara"
            }
        }
        schema_items.append(item)
    
    return json.dumps(schema_items, indent=4)

def build_grid_html(projects):
    """Generates the static grid using the Vortex-style template with top-right status badges."""
    if not projects:
        return '<div class="flex flex-col items-center justify-center py-20 text-center"><h2 class="text-3xl font-bold text-gray-700 dark:text-gray-300 mb-4">No projects added yet</h2></div>'

    html_str = '''
    <div id="projectsGrid" class="projects-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mt-6" role="list">
    '''
    for p in projects:
        title = p.get('projectName', p.get('id', 'Untitled Project'))
        desc = p.get('short_description', 'No description available for this project.')
        img = p.get('image_urls', [f"https://placehold.co/600x400?text={title.replace(' ', '+')}"])[0] if p.get('image_urls') else f"https://placehold.co/600x400?text={title.replace(' ', '+')}"
        
        tech = p.get('technologies', [])
        tags = p.get('tags', [])
        keywords = ", ".join(tech + tags)
        date_pub = p.get('upload_date', '')

        # Project Status & Badge Mapping Logic
        project_status = (p.get('project_status') or 'unknown').strip().lower()
        status_badge_class = 'bg-gray-400 text-gray-800'
        status_text = p.get('project_status', 'N/A')
        
        if project_status == 'ongoing':
            status_badge_class = 'bg-yellow-500 text-yellow-900 font-bold'
            status_text = 'Ongoing'
        elif project_status == 'completed':
            status_badge_class = 'bg-green-500 text-green-900 font-bold'
            status_text = 'Completed'
        elif project_status in ['onhold', 'on hold']:
            status_badge_class = 'bg-red-500 text-red-900 font-bold'
            status_text = 'On Hold'

        tech_html = ""
        for t in tech[:4]:
            tech_html += f'<span class="bg-blue-50 dark:bg-blue-900/40 text-blue-700 dark:text-blue-200 text-xs px-2.5 py-1 rounded-md font-semibold border border-blue-100 dark:border-blue-800" itemprop="applicationCategory">{t}</span>\n                    '

        html_str += f'''
                    <!-- Project Card: {title} -->
                    <article class="project-card group bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-2xl transition-all duration-300 flex flex-col justify-between" itemscope itemtype="https://schema.org/CreativeWork" role="listitem">
                        <header>
                            <meta itemprop="datePublished" content="{date_pub}">
                            <meta itemprop="keywords" content="{html.escape(keywords)}">
                            
                            <!-- Image Container with Absolute Status Badge -->
                            <figure class="mb-5 overflow-hidden rounded-lg bg-gray-100 relative">
                                <div class="absolute top-2 right-2 px-3 py-1 text-xs rounded-full shadow-md {status_badge_class} z-10">
                                    {status_text}
                                </div>
                                <img itemprop="image" src="{img}" alt="Preview screenshot of {title} by Teja Gavara" class="w-full h-52 object-cover transform group-hover:scale-105 transition-transform duration-500 ease-out" loading="lazy" onerror="this.src='https://placehold.co/600x400?text={title.replace(' ', '+')}'">
                            </figure>

                            <h3 itemprop="name" class="text-2xl font-bold mb-3 text-gray-900 dark:text-white leading-tight">
                                <a href="projects/{p['url']}" itemprop="url" class="hover:text-blue-600 dark:hover:text-blue-400 focus:outline-none focus:underline transition-colors">
                                    {title}
                                </a>
                            </h3>
                        </header>

                        <div class="flex-grow mb-5">
                            <p itemprop="description" class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed line-clamp-3">
                                {desc}
                            </p>
                        </div>

                        <footer>
                            <div class="mb-6" aria-label="Technologies used">
                                <h4 class="sr-only">Built with</h4>
                                <div class="flex flex-wrap gap-2">
                                    {tech_html}
                                </div>
                            </div>
                            <a itemprop="url" href="projects/{p['url']}" class="inline-flex items-center justify-center w-full bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-bold py-3 px-5 rounded-lg transition-all focus:ring-4 focus:ring-blue-300 focus:outline-none" aria-label="View details about {title}">
                                View Project Details
                                <svg class="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path>
                                </svg>
                            </a>
                        </footer>
                    </article>
        '''
    html_str += '</div>'
    return html_str

def build_detail_html(project):
    """Generates ultra-SEO-optimized static individual project detail pages for high visibility and ranking."""
    title = project.get('projectName', project.get('id', 'Untitled Project'))
    desc = project.get('short_description', f'{title} - Developed by Teja Gavara.')
    images = project.get('image_urls', [])
    first_img = images[0] if images else f"https://placehold.co/600x400?text={title.replace(' ', '+')}"
    
    tags = project.get('tags', [])
    first_tag = tags[0] if tags else "Software Project"
    tag_part = f"{first_tag}" if first_tag else ""
    tech_list = project.get('technologies', [])
    keywords = ", ".join(tags + tech_list + [title, "Teja Gavara", "G Teja Portfolio", "Software Development"])
    url_slug = f"{WEBSITE_URL}/projects/{project.get('url', '')}"
    
    diff = project.get('difficulty', '').lower()
    diff_color = 'text-red-600' if diff in ['advance', 'advanced'] else 'text-yellow-500' if diff == 'intermediate' else 'text-green-600' if diff == 'beginner' else 'text-gray-700'

    inner_html = f'''
        <div class="relative flex items-center justify-center w-full mb-6 mt-0">
            <h1 class="text-blue-600 dark:text-blue-800 font-bold text-5xl sm:text-6xl m-0 text-center">{title}</h1>
            <div class="absolute right-0 sm:right-4">
                <button type="button" onclick="shareProject(this)" class="p-2.5 text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400 bg-white dark:bg-gray-800 hover:bg-blue-50 dark:hover:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-blue-500" aria-label="Share project link">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684m0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"></path>
                    </svg>
                </button>
                <span class="share-toast hidden absolute -top-8 right-0 bg-gray-900 text-white text-xs font-semibold px-2 py-1 rounded shadow-lg whitespace-nowrap z-20 transition-all">
                    Link copied!
                </span>
            </div>
        </div>

        <script>
            function shareProject(b) {{
                const u = window.location.href;
                if (navigator.share) {{
                    navigator.share({{ title: '{title}', text: 'Check out {title} by Teja Gavara:', url: u }}).catch(() => {{}});
                }} else {{
                    navigator.clipboard.writeText(u).then(() => {{
                        const t = b.nextElementSibling;
                        t.classList.remove('hidden');
                        setTimeout(() => t.classList.add('hidden'), 2000);
                    }});
                }}
            }}
        </script>

        <div class="meta-info">
            {f"<div><strong>Uploaded:</strong> {project['upload_date']}</div>" if project.get('upload_date') else ""}
            {f"<div><strong>Last Updated:</strong> {project['last_updated']}</div>" if project.get('last_updated') else ""}
            {f"<div><strong>Views:</strong> {project.get('views', 0)}</div>"}
            {f"<div><strong>{project['button_label']}s:</strong> {project.get('downloads', 0)}</div>" if project.get('button_label') and project['button_label'].lower() != 'none' else ""}
            {f'<div><strong>Difficulty:</strong> <span class="{diff_color}">{project.get("difficulty")}</span></div>' if project.get('difficulty') else ""}
        </div>

        <div class="technologies">
            <h3>Technologies Used:</h3>
            {''.join([f"<span>{t}</span>" for t in tech_list]) if tech_list else "<p>No technologies listed.</p>"}
        </div>
    '''

    if images:
        inner_html += f'''
        <h3 class="border-b-2 border-[#e0e0e0] pb-[10px] mt-[35px] mb-[20px] w-full text-[1.8em]">Project Images</h3>
        <div class="image-carousel-container relative">
            <div class="image-carousel flex transition-transform duration-500 ease-in-out" id="imageCarousel">
                {''.join([f'<img src="{img}" alt="{title} Screenshot by Teja Gavara" class="carousel-image cursor-pointer w-full flex-shrink-0 object-contain h-[450px]">' for img in images])}
            </div>
            {"""<button class="carousel-button left absolute top-1/2 left-4 transform -translate-y-1/2 bg-black/50 text-white rounded-full w-12 h-12 flex items-center justify-center hover:bg-black/80" id="prevImage">❮</button>
                <button class="carousel-button right absolute top-1/2 right-4 transform -translate-y-1/2 bg-black/50 text-white rounded-full w-12 h-12 flex items-center justify-center hover:bg-black/80" id="nextImage">❯</button>""" if len(images) > 1 else ""}
        </div>'''

    inner_html += f'''
        <h3 class="border-b-2 border-[#e0e0e0] pb-[10px] mt-[35px] mb-[20px] w-full text-[1.8em]">Project Overview</h3>
        <p class="short-description">{project.get('short_description', 'No short description provided.')}</p>
        <h3 class="border-b-2 border-[#e0e0e0] pb-[10px] mt-[35px] mb-[20px] w-full text-[1.8em]">Project Details</h3>
        <p class="long-description">{project.get('long_description', 'No detailed description provided.')}</p>
    '''

    sponsors = project.get('sponsors', [])
    if sponsors:
        inner_html += f'''
        <div class="sponsors-section">
            <h3 class="border-b-2 border-[#e0e0e0] pb-[10px] mt-[35px] mb-[20px] w-full text-[1.8em]">Our Sponsors</h3>
            <div class="sponsors-list">{''.join([f'<span class="sponsor-name">{s}</span>' for s in sponsors])}</div>
        </div>'''

    yt_url = project.get('video_url')
    if yt_url and get_youtube_id(yt_url):
        inner_html += f'''
        <h3 class="border-b-2 border-[#e0e0e0] pb-[10px] mt-[35px] mb-[20px] w-full text-[1.8em]">Project Video Demo</h3>
        <div class="video-embed relative w-full pb-[56.25%] h-0">
            <iframe src="https://www.youtube.com/embed/{get_youtube_id(yt_url)}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen class="absolute top-0 left-0 w-full h-full rounded-lg"></iframe>
        </div>'''

    members = project.get('members', [])
    if members:
        inner_html += f'''
        <div class="members-section">
            <h3 class="border-b-2 border-[#e0e0e0] pb-[10px] mt-[35px] mb-[20px] w-full text-[1.8em]">Team Members</h3>
            <div class="members-scroll-container">
                <div class="members-list">{''.join([f'<span class="member-name">{m}</span>' for m in members])}</div>
            </div>
        </div>'''

    if project.get('code'):
        code_text = project['code']
        lines = code_text.splitlines() if code_text else []
        
        filename = ''
        if lines and 'lang=' in lines[0]:
            match = re.search(r'lang=([^\s]+)', lines[0])
            if match:
                filename = match.group(1)
            lines = lines[1:]
        
        if not filename:
            filename = title.lower().replace(' ', '_')

        display_code = '\n'.join(lines)

        inner_html += f"""
        <h3 class="border-b-2 border-[#e0e0e0] pb-[10px] mt-[35px] mb-[20px] w-full text-[1.8em] flex items-center gap-2">
            <i data-lucide="code" class="w-6 h-6 text-blue-600"></i> Code Snippet
        </h3>

        <div class="code-container bg-[#1e1e1e] relative rounded-lg shadow-xl overflow-hidden border border-gray-700">
            <div class="bg-[#2d2d2d] px-4 py-2.5 flex items-center justify-between border-b border-gray-700">
                <div class="flex items-center space-x-2">
                    <span class="w-3 h-3 bg-red-500 rounded-full inline-block"></span>
                    <span class="w-3 h-3 bg-yellow-500 rounded-full inline-block"></span>
                    <span class="w-3 h-3 bg-green-500 rounded-full inline-block"></span>
                    <span class="text-s text-gray-400 ml-2 font-mono flex items-center gap-1.5">
                        <i data-lucide="file-code" class="w-3.5 h-3.5 text-blue-400"></i> {filename}
                    </span>
                </div>
                <button id="copyCodeButton" class="flex items-center gap-1.5 text-s text-gray-400 hover:text-gray-200 bg-gray-800 hover:bg-gray-700 px-2.5 py-1 rounded transition-colors duration-150" aria-label="Copy code">
                    <i data-lucide="copy" class="w-3.5 h-3.5"></i> 
                    <span>Copy</span>
                </button>
            </div>
            
            <pre class="line-numbers !bg-[#1e1e1e] !m-0 !p-4 overflow-x-auto text-gray-100 font-mono text-sm"><code class="language-javascript">{html.escape(display_code)}</code></pre>
        </div> 

        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.js"></script>
        <script>
            lucide.createIcons();
        </script>
        """

    inner_html += '<div class="action-buttons-container flex justify-center gap-4 mt-8 flex-wrap w-full">'
    if project.get('button_url'):
        inner_html += f'<a href="{project["button_url"]}" target="_blank" rel="noopener noreferrer" class="action-button bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition transform hover:scale-105" id="projectActionButton">{project.get("button_label", "View Project")}</a>'
    
    if project.get('project_status', '').lower() != 'completed':
        inner_html += f'<a href="../join_project.html?projectName={html.escape(title)}&projectId={html.escape(project.get("id", ""))}" class="action-button join-project-button bg-green-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-green-700 transition transform hover:scale-105">Join This Project</a>'
    inner_html += '</div>'

    js_script = """
    <script>
        const btn = document.getElementById('menu-btn');
        const mobileMenu = document.getElementById('mobile-menu');
        if(btn && mobileMenu) {
            btn.addEventListener('click', () => mobileMenu.classList.toggle('hidden'));
            document.addEventListener('click', (e) => {
                if (!btn.contains(e.target) && !mobileMenu.contains(e.target)) mobileMenu.classList.add('hidden');
            });
        }

        const copyBtn = document.getElementById('copyCodeButton');
        const codeBlock = document.querySelector('.code-container code');
        if (copyBtn && codeBlock) {
            copyBtn.addEventListener('click', async () => {
                try {
                    await navigator.clipboard.writeText(codeBlock.innerText);
                    copyBtn.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5"></i> <span>Copied!</span>';
                    copyBtn.classList.remove('bg-blue-600', 'hover:bg-blue-700');
                    copyBtn.classList.add('bg-green-600', 'hover:bg-green-700');
                    lucide.createIcons();
                    setTimeout(() => {
                        copyBtn.innerHTML = '<i data-lucide="copy" class="w-3.5 h-3.5"></i> <span>Copy</span>';
                        copyBtn.classList.remove('bg-green-600', 'hover:bg-green-700');
                        copyBtn.classList.add('bg-blue-600', 'hover:bg-blue-700');
                        lucide.createIcons();
                    }, 3000);
                } catch (err) {
                    console.error('Failed to copy text: ', err);
                }
            });
        }

        const carousel = document.getElementById('imageCarousel');
        const prevBtn = document.getElementById('prevImage');
        const nextBtn = document.getElementById('nextImage');
        if (carousel) {
            let currentIndex = 0;
            const images = carousel.querySelectorAll('.carousel-image');
            const updateCarousel = () => carousel.style.transform = `translateX(-${currentIndex * 100}%)`;
            
            if (prevBtn) prevBtn.addEventListener('click', () => {
                currentIndex = currentIndex === 0 ? images.length - 1 : currentIndex - 1;
                updateCarousel();
            });
            if (nextBtn) nextBtn.addEventListener('click', () => {
                currentIndex = currentIndex === images.length - 1 ? 0 : currentIndex + 1;
                updateCarousel();
            });
        }

        const lightbox = document.getElementById('lightbox');
        const lightboxImg = document.getElementById('lightboxImage');
        const closeBtn = document.querySelector('.lightbox-close');
        let currentScale = 1;

        document.querySelectorAll('.carousel-image').forEach(img => {
            img.addEventListener('click', (e) => {
                currentScale = 1;
                if(lightboxImg) {
                    lightboxImg.style.transform = `scale(${currentScale})`;
                    lightboxImg.src = e.target.src;
                }
                if(lightbox) {
                    lightbox.classList.remove('hidden');
                    lightbox.style.display = 'flex';
                }
            });
        });

        if (closeBtn && lightbox) closeBtn.addEventListener('click', () => {
            lightbox.classList.add('hidden');
            lightbox.style.display = 'none';
        });
        
        if (lightbox) lightbox.addEventListener('click', (e) => {
            if (e.target === lightbox) {
                lightbox.classList.add('hidden');
                lightbox.style.display = 'none';
            }
        });

        if (lightboxImg) {
            lightboxImg.addEventListener('wheel', (e) => {
                e.preventDefault();
                currentScale += e.deltaY < 0 ? 0.1 : -0.1;
                currentScale = Math.max(0.5, Math.min(currentScale, 3)); 
                lightboxImg.style.transform = `scale(${currentScale})`;
            }, { passive: false });
        }
    </script>
    """

    full_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title} | {tag_part} | Teja Gavara Portfolio</title>
    
    <meta name="description" content="{html.escape(desc)}">
    <meta name="keywords" content="{html.escape(keywords)}">
    <meta name="author" content="Teja Gavara">
    
    <meta property="og:title" content="{html.escape(title)} | {tag_part} | Teja Gavara">
    <meta property="og:description" content="{html.escape(desc)}">
    <meta property="og:image" content="{first_img}">
    <meta property="og:url" content="{url_slug}">
    <meta property="og:type" content="article">

    <link rel="icon" type="image/x-icon" sizes="48x48" href="../images/favicon.ico?v=2" />
    <link rel="stylesheet" href="../output.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="../project_detail.css" />
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-okaidia.min.css" rel="stylesheet" />
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.css" rel="stylesheet" />
    <script src="https://unpkg.com/lucide@latest"></script>
    <script src="https://cdn.tailwindcss.com"></script>

    <!-- SEO Schema.org JSON-LD -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "{html.escape(title)}",
        "description": "{html.escape(desc)}",
        "image": "{first_img}",
        "keywords": "{html.escape(keywords)}",
        "datePublished": "{project.get('upload_date', '2025-01-01')}",
        "dateModified": "{project.get('last_updated', '')}",
        "author": {{
            "@type": "Person",
            "name": "Teja Gavara"
        }}
    }}
    </script>
</head>
<body class="min-h-screen flex flex-col bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-black">
    <header
        class="bg-white shadow-md py-4 px-6 md:px-10 lg:px-16 flex justify-between items-center rounded-b-lg sticky top-0 z-50 dark:bg-gray-800 dark:text-white">
        <div class="flex items-center">
        <a href="../index.html"
            class="text-2xl font-bold text-gray-800 hover:text-blue-600 dark:text-white dark:hover:text-blue-400 transition duration-300 ease-in-out">
            <span class="text-blue-600">G</span>TEJA
        </a>
        </div>

        <button id="menu-btn" class="md:hidden text-gray-700 dark:text-white focus:outline-none" aria-label="Toggle menu">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
            stroke-linejoin="round" viewBox="0 0 24 24">
            <path d="M4 6h16M4 12h16M4 18h16"></path>
        </svg>
        </button>

        <nav id="menu" class="hidden md:flex">
        <ul class="flex flex-col md:flex-row md:space-x-8">
            <li><a href="../index.html" class="block text-gray-700 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 font-medium transition duration-300 ease-in-out px-3 py-2 rounded-md">Home</a></li>
            <li><a href="../projects.html" class="block text-gray-700 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 font-medium transition duration-300 ease-in-out px-3 py-2 rounded-md">Projects</a></li>
            <li><a href="../about.html" class="block text-gray-700 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 font-medium transition duration-300 ease-in-out px-3 py-2 rounded-md">About</a></li>
            <li><a href="../contact.html" class="block text-gray-700 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 font-medium transition duration-300 ease-in-out px-3 py-2 rounded-md">Contact</a></li>
        </ul>
        </nav>
    </header>

    <nav id="mobile-menu" class="hidden bg-white shadow-md rounded-b-lg md:hidden px-6 py-4 dark:bg-gray-900">
        <ul class="flex flex-col space-y-3">
            <li><a href="../index.html" class="block text-gray-700 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 font-medium px-3 py-2 rounded-md transition duration-300">Home</a></li>
            <li><a href="../projects.html" class="block text-gray-700 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 font-medium px-3 py-2 rounded-md transition duration-300">Projects</a></li>
            <li><a href="../about.html" class="block text-gray-700 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 font-medium px-3 py-2 rounded-md transition duration-300">About</a></li>
            <li><a href="../contact.html" class="block text-gray-700 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 font-medium px-3 py-2 rounded-md transition duration-300">Contact</a></li>
        </ul>
    </nav>
    <main class="p-0 sm:p-6 md:p-10 lg:p-16">
        <div class="p-0 sm:bg-white sm:p-6 sm:rounded-lg sm:shadow-lg dark:bg-gray-900">
            <div class="back-button-container mb-6 ">
                <a href="../projects.html" class="inline-flex items-center bg-gray-200 hover:bg-gray-300 text-black font-bold py-2 px-4 rounded-md shadow-sm transition duration-300 ease-in-out dark:bg-gray-400">
                    <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="currentColor"><path d="M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6l6 6l1.41-1.41z" /></svg>
                    Back to Projects
                </a>
            </div>
            <section class="project-details-page dark:bg-gray-800 dark:text-gray-100" id="projectDetailsPage">
                {inner_html}
            </section>
        </div>
    </main>
    <div id="lightbox" class="lightbox fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 hidden" style="display: none;">
        <span class="lightbox-close absolute top-4 right-6 text-white text-5xl font-bold cursor-pointer hover:text-gray-400">&times;</span>
        <img class="lightbox-content max-w-full max-h-[80vh] rounded-lg transition-transform duration-200 cursor-grab active:cursor-grabbing" id="lightboxImage" />
    </div>
    
    {js_script}
</body>
</html>'''
    return full_html

def update_system_files():
    projects = load_projects()
    
    # 1. Update project.html Grid and JSON-LD Structured Data
    if os.path.exists(PROJECT_HTML):
        with open(PROJECT_HTML, 'r', encoding='utf-8') as f: content = f.read()
    else:
        content = '<!DOCTYPE html>\n<html>\n<head>\n<script type="application/ld+json">\n</script>\n</head>\n<body>\n<!---------- Projects Grid Start -->\n<!---------- Projects Grid End -->\n</body>\n</html>'

    grid_html = build_grid_html(projects)
    json_ld_str = f'<script type="application/ld+json">\n{build_json_ld_schema(projects)}\n</script>'

    # Replace JSON-LD block
    new_content = re.sub(r'(<!---------- JSON-LD Structured Data Start -->).*?(<!---------- JSON-LD Structured Data End -->)', rf'\1\n{json_ld_str}\n\2', content, flags=re.DOTALL)
    # Replace Projects Grid block
    new_content = re.sub(r'(<!---------- Projects Grid Start -->).*?(<!---------- Projects Grid End -->)', rf'\1\n{grid_html}\n\2', new_content, flags=re.DOTALL)

    with open(PROJECT_HTML, 'w', encoding='utf-8') as f: 
        f.write(new_content)

    # 2. Update individual project HTML files with comprehensive SEO metadata
    for p in projects:
        project_page_content = build_detail_html(p)
        with open(os.path.join(PROJECTS_DIR, p['url']), 'w', encoding='utf-8') as f:
            f.write(project_page_content)

    # 3. Update Sitemap with LastMod & Robots
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += f'  <url>\n    <loc>{WEBSITE_URL}/</loc>\n    <changefreq>weekly</changefreq>\n  </url>\n'
    for page in ['projects.html', 'about.html', 'contact.html']:
        sitemap += f'  <url>\n    <loc>{WEBSITE_URL}/{page}</loc>\n  </url>\n'
    for p in projects:
        sitemap += f'  <url>\n    <loc>{WEBSITE_URL}/projects/{p["url"]}</loc>\n'
        if p.get('last_updated'):
            sitemap += f'    <lastmod>{p["last_updated"]}</lastmod>\n'
        sitemap += f'  </url>\n'
    sitemap += '</urlset>'
    
    with open(SITEMAP_XML, 'w') as f: f.write(sitemap)
    with open(ROBOTS_TXT, 'w') as f: f.write(f"User-agent: *\nAllow: /\nSitemap: {WEBSITE_URL}/sitemap.xml")


def check_files_integrity():
    """Startup check to see if all physical HTML files exist for json entries."""
    projects = load_projects()
    missing_files = []
    
    for p in projects:
        file_path = os.path.join(PROJECTS_DIR, p['url'])
        if not os.path.exists(file_path):
            missing_files.append(p['url'])
    
    if missing_files:
        print(f"\n⚠️ WARNING: Found {len(missing_files)} missing project HTML file(s) mapped in projects.json:")
        for mf in missing_files:
            print(f" - {mf}")
        
        ans = input("\nDo you want to rebuild all content to fix missing files? (y/n): ")
        if ans.strip().lower() == 'y':
            update_system_files()
            print("✅ All missing files were successfully rebuilt and re-linked.")
        else:
            print("⚠️ Skipped rebuilding. The portfolio might display broken links.")
    else:
        update_system_files()


# --- 3. Flask API Routes ---
@app.route('/api/projects', methods=['GET'])
def get_all_projects(): return jsonify(load_projects()), 200

@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.json
    projects = load_projects()
    project_id = data.get('projectName', f"Project-{len(projects)+1}")
    file_url = generate_slug(project_id) + '.html'
    
    if any(p.get('id') == project_id for p in projects):
        return jsonify({"error": "Project already exists"}), 400

    new_project = {"id": project_id, "url": file_url}
    new_project.update(data)
    
    projects.append(new_project)
    save_projects(projects)
    update_system_files()
    
    return jsonify({"message": "Project added", "project": new_project}), 201

@app.route('/api/projects/<project_id>', methods=['PUT'])
def update_project(project_id):
    data = request.json
    projects = load_projects()
    
    for i, p in enumerate(projects):
        if p.get('id') == project_id:
            updated_project = {"id": project_id, "url": p['url']}
            updated_project.update(data)
            projects[i] = updated_project
            
            save_projects(projects)
            update_system_files()
            return jsonify({"message": "Project updated", "project": updated_project}), 200
            
    return jsonify({"error": "Project not found"}), 404

@app.route('/api/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    projects = load_projects()
    project_to_delete = next((p for p in projects if p.get('id') == project_id), None)
    
    if project_to_delete:
        projects = [p for p in projects if p.get('id') != project_id]
        save_projects(projects)
        file_path = os.path.join(PROJECTS_DIR, project_to_delete['url'])
        if os.path.exists(file_path): os.remove(file_path)
        update_system_files()
        return jsonify({"message": "Project deleted"}), 200
        
    return jsonify({"error": "Project not found"}), 404

# --- 4. Web Serve Routes ---
@app.route('/', methods=['GET'])
def serve_admin(): return send_from_directory(BASE_DIR, 'admin.html')

@app.route('/portfolio', methods=['GET'])
def serve_home(): return send_from_directory(BASE_DIR, 'projects.html')

@app.route('/<path:filename>', methods=['GET'])
def serve_base_files(filename): return send_from_directory(BASE_DIR, filename)

@app.route('/projects/<path:filename>', methods=['GET'])
def serve_project_pages(filename): return send_from_directory(PROJECTS_DIR, filename)


if __name__ == '__main__':
    check_and_create_structure()
    check_files_integrity()
    print("\n✅ System ready! Running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)