var THREE = require('three');
var TrackballControls = require('three-trackballcontrols');
const { Loader } = require('three');
var GLTFLoader=require('three-gltf-loader')
const DRACOLoader=require('three-gltf-loader')
function main() {
  const canvas = document.createElement('canvas');
  const renderer = new THREE.WebGLRenderer({canvas, alpha: true});
  renderer.setScissorTest(true);

  const sceneElements = [];
  function addScene(elem, fn) {
    const ctx = document.createElement('canvas').getContext('2d');
    elem.appendChild(ctx.canvas);
    sceneElements.push({elem, ctx, fn});
  }

  function makeScene(elem) {
    const scene = new THREE.Scene();

    const fov = 75;
    const aspect = 2;  // the canvas default
    const near = 0.1;
    const far = 100;
    const camera = new THREE.PerspectiveCamera(fov, aspect, near, far);
    camera.position.set(10,25,25);
    camera.lookAt(0, 0, 0);
    scene.add(camera);

    const controls = new TrackballControls(camera, elem);
    controls.noZoom = false;
    controls.noPan = true;

    {
      const color = 0xFFFFFF;
      const intensity = 1;
      const light = new THREE.DirectionalLight(color, intensity);
      light.position.set(-1, 2, 4);
      camera.add(light);
    }

    return {scene, camera, controls};
  }

  const sceneInitFunctionsByName = {
    //這是基本圖形
    'box': (elem) => {
      const {scene, camera, controls} = makeScene(elem);
      const geometry = new THREE.BoxBufferGeometry(1, 1, 1);
      const material = new THREE.MeshPhongMaterial({color: 'red'});
      const mesh = new THREE.Mesh(geometry, material);
      scene.add(mesh);
      return (time, rect) => {
        mesh.rotation.y = time * .1;
        camera.aspect = rect.width / rect.height;
        camera.updateProjectionMatrix();
        controls.handleResize();
        controls.update();
        renderer.render(scene, camera);
      };
    },
    'pyramid': (elem) => {
      const {scene, camera, controls} = makeScene(elem);
      const radius = .8;
      const widthSegments = 4;
      const heightSegments = 2;
      const geometry = new THREE.SphereBufferGeometry(radius, widthSegments, heightSegments);
      const material = new THREE.MeshPhongMaterial({
        color: 'blue',
        flatShading: true,
      });
      const mesh = new THREE.Mesh(geometry, material);
      scene.add(mesh);
      return (time, rect) => {
        mesh.rotation.y = time * .1;
        camera.aspect = rect.width / rect.height;
        camera.updateProjectionMatrix();
        controls.handleResize();
        controls.update();
        renderer.render(scene, camera);
      };
    },
    'insideS': (elem) => {
      const loader= new GLTFLoader();

// Load a glTF resource
loader.load(
	// resource URL
	'./house/insideS.glb',
  // called when the resource is loaded
	function ( gltf ) {

    scene.add( gltf.scene );
    
    //gltf.scene.scale.set(100,100,100)
		gltf.animations; // Array<THREE.AnimationClip>
		gltf.scene; // THREE.Group
		gltf.scenes; // Array<THREE.Group>
		gltf.cameras; // Array<THREE.Camera>
    gltf.asset; // Object
	},
	// called while loading is progressing
	function ( xhr ) {

		console.log( ( xhr.loaded / xhr.total * 100 ) + '% loaded' );

	},
	// called when loading has errors
	function ( error ) {

		console.log( 'An error happened' );

	}
);

    const {scene, camera, controls} = makeScene(elem);
    const geometry = new THREE.BoxBufferGeometry(0, 0, 0);
    const material = new THREE.MeshPhongMaterial({color:"transparent"});
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);
        return (time, rect) => {
        mesh.rotation.y = time * .1;
        camera.aspect = rect.width / rect.height ;
        camera.updateProjectionMatrix();
   
        controls.handleResize();
        controls.update();
        renderer.render(scene, camera);
      };
    },
    'manCamera': (elem) => {
      const loader= new GLTFLoader();
// Load a glTF resource
loader.load(
	// resource URL
	'./house/manCamera.glb',
  // called when the resource is loaded
	function ( gltf ) {

    scene.add( gltf.scene );
    
    //gltf.scene.scale.set(100,100,100)
		gltf.animations; // Array<THREE.AnimationClip>
		gltf.scene; // THREE.Group
		gltf.scenes; // Array<THREE.Group>
		gltf.cameras; // Array<THREE.Camera>
    gltf.asset; // Object
	},
	function ( xhr ) {

		console.log( ( xhr.loaded / xhr.total * 100 ) + '% loaded' );

	},
	function ( error ) {

		console.log( 'An error happened' );

	}
);

    const {scene, camera, controls} = makeScene(elem);
    const geometry = new THREE.BoxBufferGeometry(0, 0, 0);
    const material = new THREE.MeshPhongMaterial({color:"transparent"});
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);
        return (time, rect) => {
        mesh.rotation.y = time * .1;
        camera.aspect = rect.width / rect.height ;
        camera.updateProjectionMatrix();
   
        controls.handleResize();
        controls.update();
        renderer.render(scene, camera);
      };
    },
    
  };

  document.querySelectorAll('[data-diagram]').forEach((elem) => {
    const sceneName = elem.dataset.diagram;
    const sceneInitFunction = sceneInitFunctionsByName[sceneName];
    const sceneRenderFunction = sceneInitFunction(elem);
    addScene(elem, sceneRenderFunction);
  });

  function render(time) {
    time *= 0.001;

    for (const {elem, fn, ctx} of sceneElements) {
      const rect = elem.getBoundingClientRect();
      const {left, right, top, bottom, width, height} = rect;
      const rendererCanvas = renderer.domElement;

      const isOffscreen =
          bottom < 0 ||
          top > window.innerHeight ||
          right < 0 ||
          left > window.innerWidth;

      if (!isOffscreen) {
        if (rendererCanvas.width < width || rendererCanvas.height < height) {
          renderer.setSize(width, height, false);
        }

        if (ctx.canvas.width !== width || ctx.canvas.height !== height) {
          ctx.canvas.width = width;
          ctx.canvas.height = height;
        }

        renderer.setScissor(0, 0, width, height);
        renderer.setViewport(0, 0, width, height);

        fn(time, rect);
        ctx.globalCompositeOperation = 'copy';
        ctx.drawImage(
            rendererCanvas,
            0, rendererCanvas.height - height, width, height,  // src rect
            0, 0, width, height);                              // dst rect
      }
    }

    requestAnimationFrame(render);
  }

  requestAnimationFrame(render);
}

main();
