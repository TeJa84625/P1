let yourUpiId = null;
let formURLTemplate = null;

async function fetchConfig() {
    try {
        const response = await fetch('/info.json');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const config = await response.json();
        
        yourUpiId = config.upi;
        formURLTemplate = config.form;
        
    } catch (error) {
        console.error('Error fetching configuration from /info.json:', error);
        alert('Failed to load project configuration. Please check the console for details.');
        yourUpiId = 'error@upi'; 
        formURLTemplate = null;
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    await fetchConfig(); 
    
    if (!yourUpiId || !formURLTemplate) {
        console.error("Essential configuration (UPI ID or Form URL) is missing after fetch.");
        return; 
    }
    
    const pageHeading = document.getElementById('pageHeading');
    const formProjectTitle = document.getElementById('formProjectTitle');
    const backToProjectButton = document.getElementById('backToProjectButton');

    const userNameInput = document.getElementById('userName');
    const userEmailInput = document.getElementById('userEmail');
    const userMessageInput = document.getElementById('userMessage');
    const isSponsorCheckbox = document.getElementById('isSponsor');
    const sponsorFieldsDiv = document.getElementById('sponsorFields');
    const fundAmountInput = document.getElementById('fundAmount');
    const transactionIdInput = document.getElementById('transactionId');
    const joinProjectForm = document.getElementById('joinProjectForm');

    const qrCodeContainer = document.getElementById('qrCodeContainer');
    const qrCodeDiv = document.getElementById('qrCodeDiv');
    const paymentStatus = document.getElementById('paymentStatus');

    const urlParams = new URLSearchParams(window.location.search);
    const projectName = urlParams.get('projectName') || 'Teja`s Project';
    const projectId = urlParams.get('projectId');

    if (projectName) {
        pageHeading.textContent = `Join ${projectName}`;
        formProjectTitle.textContent = `Join "${projectName}"`;
    }

    let formattedId = projectId ? projectId.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') : '';
    backToProjectButton.href = formattedId ? `/projects/${formattedId}.html` : 'projects.html';

    const fundAmountNote = document.createElement('small');
    fundAmountNote.className = 'block mt-1 mb-5';
    fundAmountNote.textContent = '*Minimum sponsorship amount is ₹10.';
    fundAmountInput.parentNode.insertBefore(fundAmountNote, fundAmountInput.nextSibling);

    isSponsorCheckbox.addEventListener('change', () => {
        const isChecked = isSponsorCheckbox.checked;
        sponsorFieldsDiv.style.display = isChecked ? 'block' : 'none';

        fundAmountInput.required = isChecked;
        transactionIdInput.required = isChecked;

        if (!isChecked) clearQrAndButton();
    });

    fundAmountInput.addEventListener('input', () => {
        if (!isSponsorCheckbox.checked) return;

        const amount = parseFloat(fundAmountInput.value);
        if (!isNaN(amount) && amount >= 10) {
            generateUpiPaymentQr(amount);
        } else {
            clearQrAndButton();
        }
    });

    function clearQrAndButton() {
        qrCodeDiv.innerHTML = '';
        qrCodeContainer.style.display = 'none';

        const existingBtn = document.getElementById('upiPaymentBtn');
        if (existingBtn) existingBtn.remove();

        paymentStatus.textContent = '';
    }

    function generateUpiPaymentQr(amount) {
        const paymentStatus = document.getElementById('paymentStatus');
        const qrCodeDiv = document.getElementById('qrCodeDiv');
        const qrCodeContainer = document.getElementById('qrCodeContainer');
        const upiLink = document.getElementById('upi-link');
        const upiIdDisplay = document.getElementById('upi-id');

        const transactionNote = `Funding for Project: ${typeof projectName !== 'undefined' ? projectName : 'Project'}`;
        const transactionRef = 'TXN' + Date.now();
        const websiteUrl = window.location.origin;
        const logoUrl = "/images/logo.png";

        if (typeof yourUpiId === 'undefined' || !yourUpiId) {
            console.error("UPI ID is not set. Cannot generate QR code.");
            if (paymentStatus) {
                paymentStatus.textContent = "Error: UPI ID not available.";
                paymentStatus.className = "text-red-600";
            }
            return;
        }

        const upiUrl = `upi://pay?pa=${encodeURIComponent(yourUpiId)}&pn=Portfolio&tn=${encodeURIComponent(transactionNote)}&am=${amount.toFixed(2)}&cu=INR&tr=${encodeURIComponent(transactionRef)}&url=${encodeURIComponent(websiteUrl)}`;

        if (upiLink) {
            upiLink.href = upiUrl;
            upiLink.textContent = "Or click here to pay via UPI app";
            upiLink.style.display = "inline-block";
        }

        if (upiIdDisplay) {
            upiIdDisplay.textContent = yourUpiId;
        }

        if (qrCodeDiv && qrCodeContainer) {
            qrCodeDiv.innerHTML = '';
            qrCodeContainer.style.display = 'flex';

            if (typeof QRCodeStyling !== 'undefined') {
                const qrCode = new QRCodeStyling({
                    width: 200,
                    height: 200,
                    type: "svg",
                    data: upiUrl,
                    image: logoUrl,
                    dotsOptions: {
                        color: "#000000",
                        type: "classy-rounded"
                    },
                    backgroundOptions: {
                        color: "#ffffff",
                    },
                    imageOptions: {
                        crossOrigin: "anonymous",
                        margin: 5,
                        imageSize: 0.4
                    }
                });

                qrCode.append(qrCodeDiv);
                qrCodeDiv.removeAttribute('title');

            } else {
                if (paymentStatus) {
                    paymentStatus.textContent = "QR Library Error: 'qr-code-styling' script is missing.";
                    paymentStatus.className = "text-red-600";
                }
            }
        }
    }
    
    joinProjectForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const userName = userNameInput.value.trim();
    const userEmail = userEmailInput.value.trim();
    const userMessage = userMessageInput.value.trim();
    const isSponsor = isSponsorCheckbox.checked;
    const amount = isSponsor ? fundAmountInput.value.trim() : "#";
    const transactionId = isSponsor ? transactionIdInput.value.trim() : "#";

    if (isSponsor) {
        if (!amount || isNaN(amount) || parseFloat(amount) < 10) {
            alert("Minimum sponsorship amount is ₹10.");
            return;
        }
        if (!transactionId || transactionId.length !== 23) {
            alert("Please enter a valid 23-character Transaction ID.");
            return;
        }
    }

    if (formURLTemplate) {
        const formURL = formURLTemplate
            .replace("(a)", encodeURIComponent(projectName))
            .replace("(b)", encodeURIComponent(userName))
            .replace("(c)", encodeURIComponent(userEmail))
            .replace("(d)", encodeURIComponent(userMessage))
            .replace("(e)", encodeURIComponent(amount))
            .replace("(f)", encodeURIComponent(transactionId));
        
        try {
            await fetch(formURL, {
                method: 'POST',
                mode: 'no-cors' 
            });

            joinProjectForm.reset();
            sponsorFieldsDiv.style.display = 'none';
            qrCodeContainer.style.display = 'none';
            qrCodeDiv.innerHTML = '';
            const existingBtn = document.getElementById('upiPaymentBtn');
            if (existingBtn) existingBtn.remove();
            
            showThankYouModal(isSponsor, projectName);
        } catch (error) {
            console.error("Form submission failed:", error);
            alert("Failed to submit. Please try again.");
        }
    } else {
        console.error('Form URL template is not available');
        alert("Submission failed: Form configuration error.");
    }
});


    function showThankYouModal(isSponsor, projectName) {
    const modal = document.getElementById('thankYouModal');
    const content = document.getElementById('thankYouContent');

    content.classList.remove('scale-90', 'opacity-0');
    content.classList.add('scale-100', 'opacity-100');

    if (isSponsor) {
        content.innerHTML = `
            <h2 class="text-green-600 text-3xl font-semibold mb-3">🎉 Thanks for funding!</h2>
            <p class="text-gray-700 text-lg">We’ll review your transaction and add you to our sponsors list.</p>
            <p class="text-gray-600 mt-3">Feel free to contact us for any help.</p>
        `;

        triggerBlastEffect();
    } else {
        content.innerHTML = `
            <h2 class="text-blue-600 text-2xl font-semibold mb-2">🙌 Thanks for joining!</h2>
            <p class="text-gray-700">We’ll review your application and respond shortly.</p>
            <p class="text-gray-600 mt-2">Welcome to the <strong>${projectName}</strong> team!</p>
        `;
    }

    modal.classList.remove('hidden');
    modal.classList.add('flex');

    setTimeout(() => {
        modal.classList.add('hidden');

        if (typeof $ !== 'undefined' && $.confetti) {
            $.confetti.stop();
        }
    }, 6000);
    }
    
    function triggerBlastEffect() {
    const blastContainer = document.getElementById('blastContainer');
    const PARTICLE_COUNT = 128;
    const PARTICLE_SIZE = {w: 8, h: 6};
    const containerWidth = 1024; 
    const containerHeight = 700;
    const centerX = containerWidth / 2;
    const centerY = containerHeight / 2;
    const colors = ['bg-yellow-400', 'bg-red-500', 'bg-orange-500', 'bg-white'];

    blastContainer.innerHTML = '';
    const particles = [];

    for (let i = 0; i < PARTICLE_COUNT; i++) {
        const p = document.createElement('div');
        p.classList.add('absolute', 'rounded-sm', colors[Math.floor(Math.random() * colors.length)]);

        Object.assign(p.style, {
            width: PARTICLE_SIZE.w + 'px',
            height: PARTICLE_SIZE.h + 'px',
            left: (centerX - PARTICLE_SIZE.w/2) + 'px',
            top: (centerY - PARTICLE_SIZE.h/2) + 'px',
            opacity: '0',
            transformOrigin: 'center center',
        });

        blastContainer.appendChild(p);
        particles.push(p);
    }

    function easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }

    function cubicBezier(p0, c0, c1, p1, t) {
        const nt = 1 - t;
        return {
            x: nt**3*p0.x + 3*nt**2*t*c0.x + 3*nt*t**2*c1.x + t**3*p1.x,
            y: nt**3*p0.y + 3*nt**2*t*c0.y + 3*nt*t**2*c1.y + t**3*p1.y
        };
    }

    const paths = particles.map(() => ({
        p0: {x: centerX, y: centerY},
        p1: {x: centerX + (Math.random() - 0.5) * containerWidth * 0.2, y: centerY - Math.random() * containerHeight * 0.5},
        p2: {x: Math.random() * containerWidth, y: centerY - Math.random() * containerHeight * 0.2},
        p3: {x: Math.random() * containerWidth, y: containerHeight + 128}
    }));

    const start = performance.now();

    function animate(time) {
        const duration = 5000;
        const elapsed = time - start;
        const t = Math.min(elapsed / duration, 1);
        const easedT = easeOutCubic(t);

        particles.forEach((p, i) => {
            const path = paths[i];
            const pos = cubicBezier(path.p0, path.p1, path.p2, path.p3, easedT); 
            
            p.style.left = `${pos.x - PARTICLE_SIZE.w/2}px`;
            p.style.top = `${pos.y - PARTICLE_SIZE.h/2}px`;
            p.style.opacity = '1';
            p.style.transform = `rotate(${easedT * 720}deg) scaleY(${Math.abs(Math.cos(Math.PI * easedT * 5)).toFixed(2)})`;
        });

        if (t < 1) {
            requestAnimationFrame(animate);
        } else {
            blastContainer.innerHTML = '';
        }
    }

    requestAnimationFrame(animate);
}

    // FIX: Moved the transactionIdInput listener inside DOMContentLoaded scope
    transactionIdInput.addEventListener('input', () => {
        const transactionId = transactionIdInput.value.trim();
        const isValid = transactionId.length === 23;

        if (!isValid) {
            paymentStatus.textContent = "Transaction ID must be exactly 23 characters.";
            paymentStatus.style.color = "red";
        } else {
            paymentStatus.textContent = "Transaction ID is valid.";
            paymentStatus.style.color = "green";
        }
    });

});