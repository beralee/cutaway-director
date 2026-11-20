import * as THREE from "three";
import { gsap } from "gsap";

const width = 1280, height = 720;
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x11272c);
const camera = new THREE.PerspectiveCamera(38, width / height, .1, 100);
camera.setViewOffset(width, height, -210, 0, width, height);
const renderer = new THREE.WebGLRenderer({ canvas: document.querySelector("#world"), antialias: true });
renderer.setSize(width, height, false);
const root = new THREE.Group();
scene.add(root);
const soft = new THREE.HemisphereLight(0xfff5dd, 0x35464c, 2);
const key = new THREE.DirectionalLight(0xffeed0, 3);
key.position.set(-3, 7, 5);
scene.add(soft, key);

function part(geometry, color, y) {
  const mesh = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({ color, roughness: .48, metalness: .13 }));
  mesh.position.y = y;
  root.add(mesh);
  return mesh;
}
function ring(radius, thickness, color, y) {
  const mesh = part(new THREE.TorusGeometry(radius, thickness, 20, 96), color, y);
  mesh.rotation.x = Math.PI / 2;
  return mesh;
}
part(new THREE.CylinderGeometry(1.48, 1.35, .34, 96), 0x69a39d, -.62);
ring(1.19, .20, 0x6aa8a1, -.43);
const seal = ring(1.19, .095, 0xf39f45, -.18);
const lid = part(new THREE.CylinderGeometry(1.49, 1.46, .26, 96), 0xabcac1, .04);
const clamp = x => Math.min(1, Math.max(0, x));
function ease(start, end, time) {
  const x = clamp((time - start) / (end - start));
  return x*x*(3-2*x);
}
const anchor = new THREE.Vector3();
const annotation = document.querySelector("#annotation");
const leader = document.querySelector("#leader");
const pin = document.querySelector("#pin");
const label = document.querySelector("#label");

function drawAt(time) {
  const lift = ease(.50, 3.30, time) - ease(7.35, 9.55, time);
  const expose = ease(1.70, 3.80, time) - ease(6.9, 8.85, time);
  lid.position.y = .04 + lift * 1.62;
  seal.position.y = -.18 + expose * .57;
  const approach = ease(.1, 3.85, time) - ease(6.9, 9.8, time);
  camera.position.set(4.3 - .52*approach, 3.2 + .45*approach, 6.4 - .65*approach);
  camera.lookAt(0, .42, 0);
  camera.updateMatrixWorld();
  anchor.set(1.19, seal.position.y, 0).project(camera);
  const x = (1 + anchor.x) * width / 2, y = (1 - anchor.y) * height / 2;
  leader.setAttribute("d", `M${x},${y} l55,-22 h62`);
  pin.setAttribute("cx", x); pin.setAttribute("cy", y);
  label.setAttribute("x", x + 61); label.setAttribute("y", y - 32);
  annotation.setAttribute("opacity", ease(3.85, 4.22, time) - ease(6.25, 6.75, time));
  renderer.render(scene, camera);
}

// The projection and callout derive from one clock, including backward seeks.
let seconds = 0;
const clock = {
  get seconds() { return seconds; },
  set seconds(value) {
    if (value !== seconds) { seconds = value; drawAt(value); }
  },
};
drawAt(0);
const timeline = gsap.timeline({ paused: true });
timeline.fromTo(clock, { seconds: 0 }, {
  seconds: 10, duration: 10, ease: "none",
}, 0);
window.addEventListener("hf-seek", event => {
  if (Number.isFinite(event.detail?.time)) clock.seconds = event.detail.time;
});
window.__timelines = window.__timelines || {};
window.__timelines.main = timeline;
