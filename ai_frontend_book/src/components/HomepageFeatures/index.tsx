import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  description: ReactNode;
  to?: string; // Optional link for cards
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Module 1: The Robotic Nervous System (ROS 2)',
    description: (
      <>
        Learn ROS 2 fundamentals, Python AI agents, and URDF basics - the foundation of connecting AI logic to humanoid robot control.
      </>
    ),
    to: '/docs/module1/intro',
  },
  {
    title: 'Module 2: The Digital Twin (Gazebo & Unit)',
    description: (
      <>
        Master simulated environments with Gazebo physics and Unity interaction to test and validate AI-robot systems without requiring physical hardware.
      </>
    ),
    to: '/docs/module2/intro',
  },
  {
    title: 'Module 3: The AI-Robot Brain (NVIDIA Isaac™)',
    description: (
      <>
        Integrate advanced AI systems with robot control using NVIDIA Isaac tools for navigation, perception, and synthetic data generation.
      </>
    ),
    to: '/docs/module3/intro',
  },
  {
    title: 'Module 4: Vision-Language-Action (VLA)',
    description: (
      <>
        Implement advanced AI control systems that respond to voice commands and use LLM-based task planning for autonomous humanoid operation.
      </>
    ),
    to: '/docs/module4/intro',
  },
];

function Feature({title, description, to}: FeatureItem) {
  // Card design for all modules
  return (
    <div className={clsx('col col--3')}>
      <div className={clsx('card', styles.featureCard)}>
        <div className="card__header text--center">
          <Heading as="h3" className={styles.cardTitle}>{title}</Heading>
        </div>
        <div className="card__body">
          <p className={styles.cardDescription}>{description}</p>
        </div>
        {to && (
          <div className="card__footer text--center">
            <Link
              className="button button--primary button--block"
              to={to}
            >
              Explore Module
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
