/**
 * HIGH VALUE SALES — 3D GRAPHICS ENGINE (Three.js + WebGL)
 * Features:
 * 1. Landing Page 3D Crystal & Orbital Geometry with Mouse Parallax
 * 2. Dashboard Interactive 3D Sales Matrix:
 *    - Mode 1: Circular Orbit Matrix
 *    - Mode 2: Linear Cartesian Grid Matrix
 *    - Mode 3: Dynamic Wave Terrain
 *    - Raycasting hover tooltips with golden VIP particle sparkles
 *    - Orbit drag rotation & auto-spin toggles
 * 3. Fallbacks for Non-WebGL & Reduced Motion modes
 */

function isWebGLAvailable() {
    try {
        const canvas = document.createElement('canvas');
        return !!(window.WebGLRenderingContext && (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
    } catch (e) {
        return false;
    }
}

// -------------------------------------------------------------
// 1. LANDING PAGE 3D HERO SCENE
// -------------------------------------------------------------
function initLandingHero3D(containerId = 'landing-3d-canvas') {
    const container = document.getElementById(containerId);
    if (!container || !window.THREE) return;

    if (!isWebGLAvailable()) {
        render2DFallback(container);
        return;
    }

    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x070913, 0.032);

    const camera = new THREE.PerspectiveCamera(55, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.z = 24;

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'high-performance' });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Dynamic Lighting
    const ambientLight = new THREE.AmbientLight(0x182038, 2.8);
    scene.add(ambientLight);

    const lightCyan = new THREE.PointLight(0x06b6d4, 4.5, 70);
    lightCyan.position.set(15, 12, 12);
    scene.add(lightCyan);

    const lightPurple = new THREE.PointLight(0x8b5cf6, 4.5, 70);
    lightPurple.position.set(-15, -10, 10);
    scene.add(lightPurple);

    const lightGold = new THREE.PointLight(0xf59e0b, 3.2, 50);
    lightGold.position.set(0, 15, -6);
    scene.add(lightGold);

    // Group for all rotating objects
    const heroGroup = new THREE.Group();
    scene.add(heroGroup);

    // Central Core: Futuristic High-Value Financial Crystal (Icosahedron)
    const crystalGeo = new THREE.IcosahedronGeometry(4.5, 0);
    const crystalMat = new THREE.MeshPhysicalMaterial({
        color: 0x06b6d4,
        emissive: 0x071e3d,
        roughness: 0.1,
        metalness: 0.9,
        transmission: 0.7,
        ior: 1.6,
        transparent: true,
        opacity: 0.88,
        wireframe: false
    });
    const crystal = new THREE.Mesh(crystalGeo, crystalMat);
    heroGroup.add(crystal);

    // Glowing Wireframe Outer Cage
    const wireGeo = new THREE.IcosahedronGeometry(4.75, 1);
    const wireMat = new THREE.MeshBasicMaterial({
        color: 0x38bdf8,
        wireframe: true,
        transparent: true,
        opacity: 0.38
    });
    const wireCage = new THREE.Mesh(wireGeo, wireMat);
    heroGroup.add(wireCage);

    // Orbiting Geometric Ring 1: Torus
    const torusGeo1 = new THREE.TorusGeometry(8.0, 0.09, 16, 100);
    const torusMat1 = new THREE.MeshBasicMaterial({ color: 0x8b5cf6, transparent: true, opacity: 0.7 });
    const ring1 = new THREE.Mesh(torusGeo1, torusMat1);
    ring1.rotation.x = Math.PI / 3;
    heroGroup.add(ring1);

    // Orbiting Geometric Ring 2: Torus
    const torusGeo2 = new THREE.TorusGeometry(10.2, 0.07, 16, 100);
    const torusMat2 = new THREE.MeshBasicMaterial({ color: 0x22d3ee, transparent: true, opacity: 0.5 });
    const ring2 = new THREE.Mesh(torusGeo2, torusMat2);
    ring2.rotation.y = Math.PI / 4;
    heroGroup.add(ring2);

    // Floating Data Nodes (Small Octahedrons)
    const nodeCount = 16;
    const nodes = [];
    const nodeGeo = new THREE.OctahedronGeometry(0.45, 0);
    const nodeMat = new THREE.MeshStandardMaterial({
        color: 0xf59e0b,
        emissive: 0xd97706,
        roughness: 0.2,
        metalness: 0.9
    });

    for (let i = 0; i < nodeCount; i++) {
        const node = new THREE.Mesh(nodeGeo, nodeMat);
        const angle = (i / nodeCount) * Math.PI * 2;
        const radius = 7.0 + Math.sin(i * 1.5) * 2.2;
        node.position.set(
            Math.cos(angle) * radius,
            (Math.sin(i * 2.5) * 3.0),
            Math.sin(angle) * radius
        );
        node.userData = { angle, speed: 0.007 + (i % 3) * 0.003, radius, yOffset: node.position.y };
        heroGroup.add(node);
        nodes.push(node);
    }

    // Particle Constellation Field
    const particleCount = 500;
    const particleGeo = new THREE.BufferGeometry();
    const posArray = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount * 3; i += 3) {
        posArray[i] = (Math.random() - 0.5) * 80;
        posArray[i + 1] = (Math.random() - 0.5) * 60;
        posArray[i + 2] = (Math.random() - 0.5) * 70;
    }
    particleGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    const particleMat = new THREE.PointsMaterial({
        size: 0.18,
        color: 0x67e8f9,
        transparent: true,
        opacity: 0.7
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    scene.add(particles);

    // Mouse Parallax Interaction
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;
    const windowHalfX = window.innerWidth / 2;
    const windowHalfY = window.innerHeight / 2;

    function onMouseMove(event) {
        mouseX = (event.clientX - windowHalfX) * 0.0007;
        mouseY = (event.clientY - windowHalfY) * 0.0007;
    }
    window.addEventListener('mousemove', onMouseMove, { passive: true });

    function onResize() {
        if (!container) return;
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    }
    window.addEventListener('resize', onResize);

    // Animation Loop
    let isRunning = true;
    function animate() {
        if (!isRunning) return;
        requestAnimationFrame(animate);

        targetX += (mouseX - targetX) * 0.05;
        targetY += (mouseY - targetY) * 0.05;

        heroGroup.rotation.y += 0.004;
        heroGroup.rotation.x = targetY * 1.5;
        heroGroup.rotation.z = targetX * 1.2;

        wireCage.rotation.y -= 0.006;
        ring1.rotation.z += 0.005;
        ring2.rotation.x += 0.004;

        nodes.forEach(node => {
            node.userData.angle += node.userData.speed;
            node.position.x = Math.cos(node.userData.angle) * node.userData.radius;
            node.position.z = Math.sin(node.userData.angle) * node.userData.radius;
            node.position.y = node.userData.yOffset + Math.sin(Date.now() * 0.002 + node.userData.radius) * 0.7;
            node.rotation.x += 0.02;
            node.rotation.y += 0.03;
        });

        particles.rotation.y += 0.0003;
        renderer.render(scene, camera);
    }
    animate();

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        isRunning = false;
        renderer.render(scene, camera);
    }
}

// -------------------------------------------------------------
// 2. DASHBOARD 3D INTERACTIVE SALES MATRIX (With Multiple Modes)
// -------------------------------------------------------------
function initDashboard3DMatrix(containerId = 'dashboard-3d-canvas', dataUrl = '/api/analytics') {
    const container = document.getElementById(containerId);
    if (!container || !window.THREE) return;

    if (!isWebGLAvailable()) {
        render2DFallback(container);
        return;
    }

    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x070913, 0.028);

    const camera = new THREE.PerspectiveCamera(50, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(0, 15, 28);
    camera.lookAt(0, 3, 0);

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'high-performance' });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 1.4);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0x38bdf8, 2.6);
    dirLight.position.set(15, 25, 20);
    scene.add(dirLight);

    const dirPurple = new THREE.DirectionalLight(0xa855f7, 2.2);
    dirPurple.position.set(-15, 20, -10);
    scene.add(dirPurple);

    // Matrix Group
    const matrixGroup = new THREE.Group();
    scene.add(matrixGroup);

    // Floor Grid
    const gridHelper = new THREE.GridHelper(34, 22, 0x06b6d4, 0x1e293b);
    gridHelper.position.y = 0;
    scene.add(gridHelper);

    // Active visual mode: 'orbit' | 'grid' | 'wave'
    let currentLayoutMode = 'orbit';

    const interactiveBars = [];
    const tooltip = document.getElementById('canvas-3d-tooltip');

    fetch(dataUrl)
        .then(res => res.json())
        .then(payload => {
            if (payload.status !== 'success') return;

            const barsData = payload.bars_3d || [];
            const curr = payload.currency || '₹';

            if (barsData.length === 0) {
                const emptyGeo = new THREE.CylinderGeometry(2, 2, 0.5, 32);
                const emptyMat = new THREE.MeshStandardMaterial({ color: 0x334155, wireframe: true });
                const emptyMesh = new THREE.Mesh(emptyGeo, emptyMat);
                matrixGroup.add(emptyMesh);
                return;
            }

            const totalBars = barsData.length;
            const orbitRadius = 9.0;
            const cols = 6;

            barsData.forEach((item, index) => {
                const height = Math.max(1.2, item.height);

                // Bar Appearance: Gold for High-Value, Cyan/Purple for Regular
                const barColor = item.is_premium ? 0xf59e0b : (index % 2 === 0 ? 0x06b6d4 : 0x8b5cf6);
                const emissiveColor = item.is_premium ? 0x78350f : 0x0c2d48;

                const barGeo = new THREE.BoxGeometry(0.9, height, 0.9);
                const barMat = new THREE.MeshStandardMaterial({
                    color: barColor,
                    emissive: emissiveColor,
                    roughness: 0.25,
                    metalness: 0.75,
                    transparent: true,
                    opacity: 0.92
                });

                const barMesh = new THREE.Mesh(barGeo, barMat);

                // Compute Layout Positions for all 3 Modes:
                // 1. Orbit Position
                const orbitAngle = (index / totalBars) * Math.PI * 2;
                const orbitX = Math.cos(orbitAngle) * (orbitRadius - (index % 2) * 2.2);
                const orbitZ = Math.sin(orbitAngle) * (orbitRadius - (index % 2) * 2.2);

                // 2. Cartesian Grid Position
                const row = Math.floor(index / cols);
                const col = index % cols;
                const gridX = (col - (cols - 1) / 2) * 2.2;
                const gridZ = (row - (Math.ceil(totalBars / cols) - 1) / 2) * 2.2;

                // 3. Wave Position (Linear timeline spread with sine elevation)
                const waveSpread = (index - totalBars / 2) * 1.3;
                const waveZ = Math.sin(index * 0.45) * 4.5;

                barMesh.position.set(orbitX, height / 2, orbitZ);

                barMesh.userData = {
                    product: item.product,
                    amount: item.amount,
                    category: item.category,
                    date: item.date,
                    is_premium: item.is_premium,
                    currency: curr,
                    baseHeight: height,
                    positions: {
                        orbit: { x: orbitX, y: height / 2, z: orbitZ },
                        grid: { x: gridX, y: height / 2, z: gridZ },
                        wave: { x: waveSpread, y: height / 2, z: waveZ }
                    }
                };

                // Add crown cone on top of high-value deals
                if (item.is_premium) {
                    const crownGeo = new THREE.ConeGeometry(0.35, 0.6, 6);
                    const crownMat = new THREE.MeshBasicMaterial({ color: 0xfef08a });
                    const crownMesh = new THREE.Mesh(crownGeo, crownMat);
                    crownMesh.position.y = height / 2 + 0.45;
                    crownMesh.rotation.x = Math.PI;
                    barMesh.add(crownMesh);
                }

                matrixGroup.add(barMesh);
                interactiveBars.push(barMesh);
            });
        })
        .catch(err => {
            console.warn("3D Analytics API data error:", err);
        });

    // Layout Transition Function
    window.switch3DLayoutMode = function(modeName) {
        currentLayoutMode = modeName;
        interactiveBars.forEach(bar => {
            const target = bar.userData.positions[modeName];
            if (target && window.gsap) {
                gsap.to(bar.position, {
                    x: target.x,
                    y: target.y,
                    z: target.z,
                    duration: 0.8,
                    ease: 'power2.inOut'
                });
            } else if (target) {
                bar.position.set(target.x, target.y, target.z);
            }
        });
    };

    // Raycasting for interactive hover & tooltips
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2(-100, -100);
    let hoveredBar = null;

    function onPointerMove(event) {
        const rect = container.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / container.clientWidth) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / container.clientHeight) * 2 + 1;

        if (tooltip && hoveredBar) {
            tooltip.style.left = `${event.clientX - rect.left}px`;
            tooltip.style.top = `${event.clientY - rect.top - 15}px`;
        }
    }
    container.addEventListener('mousemove', onPointerMove);

    // Auto-rotation toggle
    let autoRotate = true;
    const rotateBtn = document.getElementById('btn-3d-rotate');
    if (rotateBtn) {
        rotateBtn.addEventListener('click', () => {
            autoRotate = !autoRotate;
            rotateBtn.classList.toggle('active', autoRotate);
            rotateBtn.textContent = autoRotate ? 'Auto: ON' : 'Auto: OFF';
        });
    }

    // Reset view button
    const resetBtn = document.getElementById('btn-3d-reset');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            if (window.gsap) {
                gsap.to(matrixGroup.rotation, { y: 0, duration: 0.6 });
                gsap.to(camera.position, { x: 0, y: 15, z: 28, duration: 0.6 });
            } else {
                matrixGroup.rotation.y = 0;
                camera.position.set(0, 15, 28);
                camera.lookAt(0, 3, 0);
            }
        });
    }

    // Mode Switcher Buttons
    const modeBtns = document.querySelectorAll('.btn-3d-mode');
    modeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            modeBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const mode = btn.getAttribute('data-mode');
            if (window.switch3DLayoutMode) {
                window.switch3DLayoutMode(mode);
            }
        });
    });

    // Drag to Rotate
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };

    container.addEventListener('mousedown', (e) => {
        isDragging = true;
        previousMousePosition = { x: e.clientX, y: e.clientY };
    });

    window.addEventListener('mouseup', () => {
        isDragging = false;
    });

    container.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        const deltaX = e.clientX - previousMousePosition.x;
        matrixGroup.rotation.y += deltaX * 0.007;
        previousMousePosition = { x: e.clientX, y: e.clientY };
    });

    function onResize() {
        if (!container) return;
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    }
    window.addEventListener('resize', onResize);

    // Animation Loop
    function animate() {
        requestAnimationFrame(animate);

        if (autoRotate && !isDragging) {
            matrixGroup.rotation.y += 0.003;
        }

        // Raycasting check
        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(interactiveBars, false);

        if (intersects.length > 0) {
            const hitBar = intersects[0].object;
            if (hoveredBar !== hitBar) {
                if (hoveredBar) {
                    hoveredBar.scale.set(1, 1, 1);
                    hoveredBar.material.emissiveIntensity = 1.0;
                }
                hoveredBar = hitBar;
                hoveredBar.scale.set(1.25, 1.08, 1.25);
                hoveredBar.material.emissiveIntensity = 2.5;

                if (tooltip && hoveredBar.userData) {
                    const u = hoveredBar.userData;
                    const badge = u.is_premium 
                        ? '<span style="color:#f59e0b;font-weight:bold;">★ HIGH-VALUE DEAL</span>' 
                        : '<span style="color:#38bdf8;">REGULAR SALE</span>';
                    
                    tooltip.innerHTML = `
                        <div style="font-weight:700;font-size:0.88rem;margin-bottom:2px;">${u.product}</div>
                        <div style="color:#94a3b8;font-size:0.75rem;margin-bottom:4px;">${u.category} &bull; ${badge}</div>
                        <div style="font-size:1.05rem;font-weight:800;color:#22d3ee;">${u.currency}${Number(u.amount).toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
                        <div style="color:#64748b;font-size:0.72rem;margin-top:2px;">Recorded: ${u.date}</div>
                    `;
                    tooltip.style.display = 'block';
                }
            }
        } else {
            if (hoveredBar) {
                hoveredBar.scale.set(1, 1, 1);
                hoveredBar.material.emissiveIntensity = 1.0;
                hoveredBar = null;
                if (tooltip) tooltip.style.display = 'none';
            }
        }

        renderer.render(scene, camera);
    }
    animate();
}

// -------------------------------------------------------------
// 3. 2D FALLBACK FOR NON-WEBGL DEVICES OR REDUCED MOTION
// -------------------------------------------------------------
function render2DFallback(container) {
    if (!container) return;
    container.innerHTML = `
        <div style="width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;background:radial-gradient(circle, #0e162f 0%, #070913 100%);color:#94a3b8;text-align:center;padding:2rem;">
            <div style="width:64px;height:64px;border-radius:16px;background:rgba(6,182,212,0.15);border:1px solid #06b6d4;display:flex;align-items:center;justify-content:center;color:#22d3ee;font-size:1.8rem;margin-bottom:1rem;">
                ✦
            </div>
            <h4 style="color:#ffffff;margin-bottom:0.4rem;">High Value Sales 2D Perspective Active</h4>
            <p style="font-size:0.85rem;max-width:320px;">Lightweight hardware mode engaged for optimal battery & rendering performance.</p>
        </div>
    `;
}

document.addEventListener('DOMContentLoaded', () => {
    initLandingHero3D('landing-3d-canvas');
    initDashboard3DMatrix('dashboard-3d-canvas');
});
