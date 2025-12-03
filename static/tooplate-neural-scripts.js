// JavaScript Document

// Neural Network Background Animation
        const canvas = document.getElementById('neural-bg');
        const ctx = canvas.getContext('2d');
        let nodes = [];
        let mouse = { x: 0, y: 0 };

        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        class Node {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.vx = (Math.random() - 0.5) * 0.5;
                this.vy = (Math.random() - 0.5) * 0.5;
                this.radius = Math.random() * 3 + 1;
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;

                if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
                if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = '#00ffff';
                ctx.fill();
            }
        }

        function init() {
            nodes = [];
            for (let i = 0; i < 100; i++) {
                nodes.push(new Node(
                    Math.random() * canvas.width,
                    Math.random() * canvas.height
                ));
            }
        }

        function connectNodes() {
            for (let i = 0; i < nodes.length; i++) {
                for (let j = i + 1; j < nodes.length; j++) {
                    const dx = nodes[i].x - nodes[j].x;
                    const dy = nodes[i].y - nodes[j].y;
                    const distance = Math.sqrt(dx * dx + dy * dy);

                    if (distance < 150) {
                        ctx.beginPath();
                        ctx.moveTo(nodes[i].x, nodes[i].y);
                        ctx.lineTo(nodes[j].x, nodes[j].y);
                        ctx.strokeStyle = `rgba(0, 255, 255, ${1 - distance / 150})`;
                        ctx.lineWidth = 0.5;
                        ctx.stroke();
                    }
                }
            }
        }

        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            nodes.forEach(node => {
                node.update();
                node.draw();
            });

            connectNodes();
            requestAnimationFrame(animate);
        }

        // Initialize and start animation
        init();
        animate();

        // Handle window resize
        window.addEventListener('resize', () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            init();
        });

        // Mouse move effect
        window.addEventListener('mousemove', (e) => {
            mouse.x = e.clientX;
            mouse.y = e.clientY;
        });

        // Mobile menu toggle
        const mobileToggle = document.getElementById('mobile-toggle');
        const navMenu = document.getElementById('nav-menu');

        mobileToggle.addEventListener('click', () => {
            mobileToggle.classList.toggle('active');
            navMenu.classList.toggle('active');
        });

        // Close mobile menu when clicking on a link
        document.querySelectorAll('.nav-menu a').forEach(link => {
            link.addEventListener('click', () => {
                mobileToggle.classList.remove('active');
                navMenu.classList.remove('active');
            });
        });

        // Smooth scroll
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });

        // Navbar scroll effect
        window.addEventListener('scroll', () => {
            const navbar = document.getElementById('navbar');
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }

            // Fade in sections
            const sections = document.querySelectorAll('.fade-in');
            sections.forEach(section => {
                const rect = section.getBoundingClientRect();
                if (rect.top < window.innerHeight * 0.8) {
                    section.classList.add('visible');
                }
            });
        });

        // Form submission
        document.querySelector('.contact-form').addEventListener('submit', (e) => {
            e.preventDefault();
            alert('Message sent! (This is a demo)');
        });

        // Filter functionality
        console.log('Initializing filters...');
        const filterButtons = document.querySelectorAll('.filter-btn');
        const projectCards = document.querySelectorAll('.projects-grid a');
        console.log('Found', filterButtons.length, 'buttons and', projectCards.length, 'cards');

        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                const filter = button.getAttribute('data-filter');
                console.log('Clicked filter:', filter);

                // Remove active class from all buttons
                filterButtons.forEach(btn => btn.classList.remove('active'));
                // Add active class to clicked button
                button.classList.add('active');

                // Filter cards
                let visibleCount = 0;
                projectCards.forEach(card => {
                    const description = card.getAttribute('data-tooltip').toLowerCase();
                    let show = false;
                    if (filter === 'all') {
                        show = true;
                    } else if (filter === 'genshin' && description.includes('genshin')) {
                        show = true;
                    } else if (filter === 'wuthering' && description.includes('wuthering')) {
                        show = true;
                    } else if (filter === 'zenless' && description.includes('zenless')) {
                        show = true;
                    } else if (filter === 'honkai' && description.includes('honkai')) {
                        show = true;
                    } else if (filter === 'series' && (description.includes('hazbin') || description.includes('league'))) {
                        show = true;
                    } else if (filter === 'otros' && !description.includes('genshin') && !description.includes('wuthering') && !description.includes('zenless') && !description.includes('honkai') && !description.includes('hazbin') && !description.includes('league')) {
                        show = true;
                    }
                    card.style.display = show ? 'block' : 'none';
                    if (show) visibleCount++;
                });
                console.log('Visible cards:', visibleCount);
            });
        });